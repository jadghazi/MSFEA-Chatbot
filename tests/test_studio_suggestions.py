"""Answer suggestions cannot invent facts or bypass review/publication authority."""

from __future__ import annotations

import json
from dataclasses import replace
from types import SimpleNamespace
from uuid import uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.types.json import Json

import msfea_bot.api.app as api
from msfea_bot.config import settings
from msfea_bot.curation import assistance, suggestions
from msfea_bot.curation.assistance import Intake
from msfea_bot.llm import LLMRateLimitError
from msfea_bot.retrieval.store import indexed_generation
from msfea_bot.curation.revisions import create_draft
from msfea_bot.curation.validation import start_validation
from msfea_bot.curation.workspace import schedule
import test_curation_publication

_publication_database = test_curation_publication.publication_database
ORIGINAL = "The Approved Experience internship course is a 1-credit course."
QUESTION = "How many credits is Approved Experience, and how many credits must I complete before registering?"
INTAKE = Intake(guidance=ORIGINAL,question=QUESTION,department="all",programs=["internship"])
SOURCES = [{"id":"official","text":"The Approved Experience internship course is a 1-credit course. A student must have completed at least 90 credits before registration.","source_doc":"guidelines.md","section":"Registration","department":"all"}]


def parent(database: str, intake: Intake = INTAKE) -> str:
    job_id=uuid4().hex
    with psycopg.connect(database,autocommit=True) as conn:
        conn.execute(
            "INSERT INTO curation_assistance (id,request_key,intake,status,model,prompt_version,kb_generation,report)"
            " VALUES (%s,%s,%s,'completed','test-model',%s,%s,%s)",
            (job_id,uuid4().hex,Json(intake.model_dump()),assistance.PROMPT_VERSION,indexed_generation(),
             Json({"clarifications":["Provide the eligibility credit requirement."],"blocked":True})),
        )
    return job_id


def proposal() -> dict:
    return {"sentences":[{"text":ORIGINAL,"support_ids":["original:c1"]},
                         {"text":"A student must have completed at least 90 credits before registration.","support_ids":["source:0:c2"]}],
            "explanation":"Added the separate registration eligibility requirement from the supplied source.","missing_details":[],"claim_changes":[]}


def verification() -> dict:
    return {"unsupported_sentences":[],"all_changes_explained":True,"scope_preserved":True,
            "necessary_missing_detail_indexes":[],
            "one_focused_topic":True,"explanation":"Both credit facts are supported and the original course value is preserved."}


def model(monkeypatch: pytest.MonkeyPatch, offered: dict | None = None, verified: dict | None = None) -> list[str]:
    calls=[]
    monkeypatch.setattr(assistance,"_evidence",lambda intake:SOURCES)
    monkeypatch.setattr(assistance,"reserve_model_call",lambda job_id,model:calls.append(job_id))
    def provider(schema,model,before_request):
        def generate(prompt):
            before_request()
            content=(offered or proposal()) if schema["title"]=="ProposedAnswer" else (verified or verification())
            return SimpleNamespace(text=json.dumps(content))
        return SimpleNamespace(generate=generate)
    monkeypatch.setattr(suggestions,"get_curation_provider",provider)
    return calls


def test_numeric_and_unknown_source_facts_are_rejected_before_independent_check() -> None:
    available=suggestions.facts(INTAKE,SOURCES)
    invalid=proposal()
    invalid["sentences"][1]["text"]="A student needs 100 credits before registration."
    with pytest.raises(ValueError,match="numeric"):
        suggestions.checked_proposal(json.dumps(invalid),available,INTAKE)
    invalid["sentences"][1]["support_ids"]=["invented-source"]
    with pytest.raises(ValueError,match="unknown evidence"):
        suggestions.checked_proposal(json.dumps(invalid),available,INTAKE)


def test_pre_addition_review_request_remains_idempotent(_publication_database: str) -> None:
    key=uuid4().hex
    review_id=assistance.enqueue(INTAKE,key)
    with psycopg.connect(_publication_database) as conn:
        conn.execute("UPDATE curation_assistance SET intake=intake-'suggestion_id' WHERE id=%s",(review_id,))
    assert assistance.enqueue(INTAKE,key)==review_id


def test_existing_source_cannot_silently_replace_an_original_numeric_rule() -> None:
    conflicting=INTAKE.model_copy(update={'guidance':'The internship course is a 3-credit course.'})
    with pytest.raises(ValueError,match='numeric fact without explaining'):
        suggestions.checked_proposal(json.dumps(proposal()),suggestions.facts(conflicting,SOURCES),conflicting)


def credit_correction(intake: Intake) -> dict:
    return {"sentences":[{"text":ORIGINAL,"support_ids":["source:0:c1"]}],
            "explanation":"Proposes the current KB credit value for staff review, not a new policy approval.",
            "missing_details":[],"claim_changes":[{"original_claim_id":"original:c1","sentence_index":0,
            "reason":"The proposed credit value differs from the existing official 1-credit rule.",
            "support_ids":["source:0:c1"]}]}


@pytest.mark.parametrize('credits',[3,5])
def test_declared_source_backed_credit_correction_requires_fresh_review(
    _publication_database: str,monkeypatch: pytest.MonkeyPatch,credits: int,
) -> None:
    intake=INTAKE.model_copy(update={'guidance':f'The internship course is a {credits}-credit course.'})
    offered=credit_correction(intake)
    model(monkeypatch,offered=offered)
    parent_id=parent(_publication_database,intake)
    with psycopg.connect(_publication_database) as conn:
        conn.execute("UPDATE curation_assistance SET report=%s WHERE id=%s",(Json({'classification':'direct_conflict'}),parent_id))
    job_id=suggestions.enqueue(parent_id,None,uuid4().hex)
    assert assistance.process_next()
    job=suggestions.get(job_id)
    assert job and job['status']=='completed' and job['intake']['guidance']==intake.guidance
    assert job['report']['claim_changes'][0]['before']==intake.guidance
    assert job['report']['claim_changes'][0]['sources'][0]['text']==ORIGINAL
    assert job['report']['suggested_answer']==ORIGINAL
    fresh_id=assistance.enqueue(intake.model_copy(update={'guidance':ORIGINAL,'suggestion_id':job_id}),uuid4().hex)
    fresh=assistance.get_review(fresh_id)
    assert fresh and fresh['status']=='queued' and fresh_id!=parent_id
    with psycopg.connect(_publication_database) as conn:
        assert conn.execute('SELECT count(*) FROM curated_entries').fetchone()[0]==0
        assert conn.execute('SELECT count(*) FROM curation_validation_runs').fetchone()[0]==0


def test_claim_change_cannot_cite_disputed_input_or_reference_another_answer() -> None:
    intake=INTAKE.model_copy(update={'guidance':'The internship course is a 5-credit course.'})
    offered=credit_correction(intake)
    available=suggestions.facts(intake,SOURCES)
    offered['claim_changes'][0]['support_ids']=['original:c1']
    with pytest.raises(ValueError,match='existing KB evidence'):
        suggestions.checked_proposal(json.dumps(offered),available,intake)
    offered['claim_changes'][0]['support_ids']=['source:0:c1']
    offered['claim_changes'][0]['original_claim_id']='original:nonexistent'
    with pytest.raises(ValueError,match='unknown original guidance'):
        suggestions.checked_proposal(json.dumps(offered),available,intake)
    offered['claim_changes'][0]['original_claim_id']='original:c1'
    offered['claim_changes'][0]['sentence_index']=4
    with pytest.raises(ValueError,match='unknown suggested sentence'):
        suggestions.checked_proposal(json.dumps(offered),available,intake)


def test_numbered_original_claim_reference_is_unambiguous_without_its_prefix() -> None:
    intake=INTAKE.model_copy(update={'guidance':'The internship course is a 5-credit course.'})
    offered=credit_correction(intake)
    offered['claim_changes'][0]['original_claim_id']='c1'
    checked=suggestions.checked_proposal(json.dumps(offered),suggestions.facts(intake,SOURCES),intake)
    assert checked.claim_changes[0].original_claim_id=='original:c1'


def test_original_link_replacement_requires_explanation_and_existing_kb_link() -> None:
    intake=INTAKE.model_copy(update={'guidance':'Use https://old.example/form for the internship form.'})
    source={'text':'Use https://official.example/form for the internship form.',
            'source_doc':'forms.md','section':'Forms','department':'all'}
    available=suggestions.facts(intake,[source])
    offered={'sentences':[{'text':source['text'],'support_ids':['source:0:c1']}],
             'explanation':'Proposes the current official form link for staff review.',
             'missing_details':[],'claim_changes':[]}
    with pytest.raises(ValueError,match='URL without explaining'):
        suggestions.checked_proposal(json.dumps(offered),available,intake)
    offered['claim_changes']=[{'original_claim_id':'original:c1','sentence_index':0,
                              'reason':'The existing KB lists a different official form URL.',
                              'support_ids':['source:0:c1']}]
    assert suggestions.checked_proposal(json.dumps(offered),available,intake).claim_changes
    offered['sentences'][0]['text']='Use https://invented.example/form for the internship form.'
    with pytest.raises(ValueError,match='invented a URL'):
        suggestions.checked_proposal(json.dumps(offered),available,intake)


def test_hidden_qualifier_change_is_rejected_by_verifier(
    _publication_database: str,monkeypatch: pytest.MonkeyPatch,
) -> None:
    intake=INTAKE.model_copy(update={'guidance':'The internship must be completed in summer.'})
    source={**SOURCES[0],'text':'The internship is normally completed in summer.'}
    offered={'sentences':[{'text':source['text'],'support_ids':['source:0:c1']}],
             'explanation':'Clarified the wording.','missing_details':[],'claim_changes':[]}
    checked=verification()
    checked['all_changes_explained']=False
    model(monkeypatch,offered=offered,verified=checked)
    monkeypatch.setattr(assistance,'_evidence',lambda intake:[source])
    job_id=suggestions.enqueue(parent(_publication_database,intake),None,uuid4().hex)
    assistance.process_next()
    job=suggestions.get(job_id)
    assert job and job['status']=='failed' and 'suggested_answer' not in job['report']


@pytest.mark.parametrize('classification',['direct_conflict','supersedes'])
def test_policy_conflict_can_request_a_private_answer_suggestion(
    _publication_database: str,classification: str,
) -> None:
    review_id=parent(_publication_database)
    with psycopg.connect(_publication_database) as conn:
        conn.execute("UPDATE curation_assistance SET report=%s WHERE id=%s",(Json({'classification':classification}),review_id))
    job_id=suggestions.enqueue(review_id,None,uuid4().hex)
    job=suggestions.get(job_id)
    assert job and job['status']=='queued' and job['report']['context']['review_feedback']['classification']==classification
    with psycopg.connect(_publication_database) as conn:
        assert conn.execute('SELECT count(*) FROM curation_assistance').fetchone()[0]==2
        assert conn.execute('SELECT count(*) FROM curated_entries').fetchone()[0]==0


def test_new_links_and_cross_department_sources_are_rejected() -> None:
    available=suggestions.facts(INTAKE,SOURCES)
    invalid=proposal()
    invalid["sentences"][1]["text"]="Register at https://invented.example/form."
    with pytest.raises(ValueError,match="URL"):
        suggestions.checked_proposal(json.dumps(invalid),available,INTAKE)
    sources=[{**SOURCES[0],"department":"ece"}]
    assert all(ref.startswith('original:') for ref in suggestions.facts(INTAKE,sources))


def test_same_worker_completes_two_call_suggestion_without_creating_knowledge(
    _publication_database: str, monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls=model(monkeypatch)
    generation=indexed_generation()
    review_id=parent(_publication_database)
    key=uuid4().hex
    job_id=suggestions.enqueue(review_id,None,key)
    assert suggestions.enqueue(review_id,None,key)==job_id
    assert assistance.process_next()
    job=suggestions.get(job_id)
    assert job and job["status"]=="completed"
    assert len(calls)==2 and job["intake"]["guidance"]==ORIGINAL
    assert "90 credits" in job["report"]["suggested_answer"]
    assert indexed_generation()==generation
    with psycopg.connect(_publication_database) as conn:
        assert conn.execute('SELECT count(*) FROM curated_entries').fetchone()[0]==0


@pytest.mark.parametrize('failed_check',["unsupported_sentences","all_changes_explained","scope_preserved","one_focused_topic"])
def test_independent_rejection_never_offers_an_unverified_answer(
    _publication_database: str,monkeypatch: pytest.MonkeyPatch,failed_check: str,
) -> None:
    invalid=verification()
    invalid[failed_check]=[1] if failed_check=="unsupported_sentences" else False
    model(monkeypatch,verified=invalid)
    job_id=suggestions.enqueue(parent(_publication_database),None,uuid4().hex)
    assert assistance.process_next()
    job=suggestions.get(job_id)
    assert job and job["status"]=="failed" and job["error_code"]=="unsupported_suggestion"
    assert 'suggested_answer' not in job["report"]
    assert job['report']['rejection_reason']==invalid['explanation']


def test_missing_facts_remain_questions_without_becoming_canonical_text(
    _publication_database: str,monkeypatch: pytest.MonkeyPatch,
) -> None:
    offered={"sentences":[proposal()["sentences"][0]],"explanation":"The supplied facts do not provide office opening hours.",
             "missing_details":["What are the approved office opening hours?"],"claim_changes":[]}
    checked=verification()
    checked["necessary_missing_detail_indexes"]=[0]
    model(monkeypatch,offered=offered,verified=checked)
    job_id=suggestions.enqueue(parent(_publication_database),None,uuid4().hex)
    assistance.process_next()
    job=suggestions.get(job_id)
    assert job and job["report"]["suggested_answer"]==ORIGINAL
    assert job["report"]["missing_details"]==offered["missing_details"]


def test_optional_follow_up_is_removed_by_independent_check(
    _publication_database: str,monkeypatch: pytest.MonkeyPatch,
) -> None:
    offered=proposal()
    offered["missing_details"]=["What formatting should be used for the answer?"]
    model(monkeypatch,offered=offered)
    job_id=suggestions.enqueue(parent(_publication_database),None,uuid4().hex)
    assistance.process_next()
    job=suggestions.get(job_id)
    assert job and job["status"]=="completed" and job["report"]["missing_details"]==[]


def test_saved_revision_suggestion_keeps_failed_checks_without_rewriting_the_draft(
    _publication_database: str,monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls=model(monkeypatch)
    payload=replace(test_curation_publication._payload(),question=QUESTION,answer=ORIGINAL,
                    department='all',linked_feedback_ids=(),source_kind='admin_authored',
                    document_title='Approved Experience credits',authority_label='CDC',evidence_refs=(),
                    representative_question=QUESTION,paraphrase_question='What is the course credit value?',
                    expected_evidence='1-credit')
    entry_id,revision_id=create_draft(payload)
    review_id=parent(_publication_database,INTAKE.model_copy(update={'entry_id':entry_id}))
    with psycopg.connect(_publication_database) as conn:
        conn.execute('UPDATE curation_assistance SET accepted_revision_id=%s WHERE id=%s',(revision_id,review_id))
    run_id=start_validation(revision_id)
    failure={'cases':[{'question':QUESTION,'candidate_hit':False}]}
    with psycopg.connect(_publication_database) as conn:
        conn.execute("UPDATE curation_validation_runs SET status='failed' WHERE id=%s",(run_id,))
        conn.execute("UPDATE curation_revision_state SET state='blocked' WHERE revision_id=%s",(revision_id,))
        conn.execute("INSERT INTO curation_validation_results (run_id,step,status,details) VALUES (%s,'positive_retrieval','failed',%s)",(run_id,Json(failure)))
        schedule(conn,run_id,revision_id,'preview')
        conn.execute("UPDATE curation_workspace_jobs SET status='completed',result=%s WHERE run_id=%s",(Json({'passed':False,'previews':[{'question':QUESTION,'refused':True}]}),run_id))
    key=uuid4().hex
    job_id=suggestions.enqueue(None,revision_id,key)
    assert suggestions.enqueue(None,revision_id,key)==job_id
    assistance.process_next()
    job=suggestions.get(job_id)
    assert job and job['status']=='completed' and len(calls)==2
    assert job['report']['context']['failed_checks']==[{'step':'positive_retrieval','details':failure}]
    assert job['report']['context']['preview_feedback'][0]['result']['previews'][0]['refused']
    assert job['intake']['entry_id']==entry_id and job['intake']['guidance']==ORIGINAL
    with psycopg.connect(_publication_database) as conn:
        assert conn.execute('SELECT answer FROM curated_revisions WHERE id=%s',(revision_id,)).fetchone()[0]==ORIGINAL
        assert conn.execute('SELECT count(*) FROM curated_revisions').fetchone()[0]==1
        assert conn.execute("SELECT status FROM curation_validation_runs WHERE id=%s",(run_id,)).fetchone()[0]=='failed'


def test_official_source_correction_stays_in_source_ingestion_flow(_publication_database: str) -> None:
    _,revision_id=create_draft(test_curation_publication._payload())
    with pytest.raises(ValueError,match='source editor and ingestion'):
        suggestions.enqueue(None,revision_id,uuid4().hex)


def test_invalid_missing_detail_reference_rejects_suggestion(
    _publication_database: str,monkeypatch: pytest.MonkeyPatch,
) -> None:
    checked=verification()
    checked["necessary_missing_detail_indexes"]=[5]
    model(monkeypatch,verified=checked)
    job_id=suggestions.enqueue(parent(_publication_database),None,uuid4().hex)
    assistance.process_next()
    job=suggestions.get(job_id)
    assert job and job["status"]=="failed" and 'suggested_answer' not in job["report"]


def test_selecting_an_edited_suggestion_enqueues_fresh_review_and_records_choice(
    _publication_database: str,monkeypatch: pytest.MonkeyPatch,
) -> None:
    model(monkeypatch)
    job_id=suggestions.enqueue(parent(_publication_database),None,uuid4().hex)
    assistance.process_next()
    edited=INTAKE.model_copy(update={"guidance":ORIGINAL+" At least 90 completed credits are required before registration.","suggestion_id":job_id})
    review_id=assistance.enqueue(edited,uuid4().hex)
    review=assistance.get_review(review_id)
    assert review and review['status']=='queued' and review['intake']['suggestion_id']==job_id
    with psycopg.connect(_publication_database) as conn:
        assert conn.execute("SELECT payload->>'edited' FROM curation_events WHERE event_type='answer_suggestion_used'").fetchone()[0]=='true'
        assert conn.execute('SELECT count(*) FROM curation_validation_runs').fetchone()[0]==0


def test_changed_scope_or_stale_knowledge_requires_a_new_suggestion(
    _publication_database: str,monkeypatch: pytest.MonkeyPatch,
) -> None:
    model(monkeypatch)
    job_id=suggestions.enqueue(parent(_publication_database),None,uuid4().hex)
    assistance.process_next()
    changed=INTAKE.model_copy(update={"department":"ece","suggestion_id":job_id})
    with pytest.raises(ValueError,match='scope changed'):
        assistance.enqueue(changed,uuid4().hex)
    monkeypatch.setattr(suggestions,'indexed_generation',lambda:'changed-generation')
    with pytest.raises(ValueError,match='knowledge base changed'):
        assistance.enqueue(INTAKE.model_copy(update={"suggestion_id":job_id}),uuid4().hex)


def test_stale_queued_suggestion_never_calls_the_model(
    _publication_database: str,monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls=model(monkeypatch)
    job_id=suggestions.enqueue(parent(_publication_database),None,uuid4().hex)
    monkeypatch.setattr(suggestions,'indexed_generation',lambda:'changed-generation')
    assistance.process_next()
    job=suggestions.get(job_id)
    assert job and job['status']=='failed' and job['error_code']=='stale_index'
    assert calls==[]


def test_old_pending_suggestion_never_runs_as_a_policy_review(
    _publication_database: str,monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls=model(monkeypatch)
    job_id=suggestions.enqueue(parent(_publication_database),None,uuid4().hex)
    with psycopg.connect(_publication_database) as conn:
        conn.execute("UPDATE curation_assistance SET prompt_version='source-backed-answer-suggestion-v1' WHERE id=%s",(job_id,))
    assert not assistance.process_next()
    job=suggestions.get(job_id)
    assert job and job['status']=='failed' and job['error_code']=='stale_review'
    assert job['outdated'] and calls==[]


def test_provider_failure_preserves_original_input_and_is_not_a_policy_verdict(
    _publication_database: str,monkeypatch: pytest.MonkeyPatch,
) -> None:
    model(monkeypatch)
    def unavailable(*args,**kwargs):
        raise LLMRateLimitError('test quota')
    monkeypatch.setattr(suggestions,'get_curation_provider',unavailable)
    job_id=suggestions.enqueue(parent(_publication_database),None,uuid4().hex)
    assistance.process_next()
    job=suggestions.get(job_id)
    assert job and job['error_code']=='quota' and job['intake']['guidance']==ORIGINAL


def test_api_is_authorized_and_suggestion_is_not_an_accepted_policy_review(
    _publication_database: str,monkeypatch: pytest.MonkeyPatch,
) -> None:
    model(monkeypatch)
    monkeypatch.setattr(settings,'admin_token','test-admin')
    monkeypatch.setattr(settings,'curation_worker_token','private-worker')
    client=TestClient(api.app)
    body={'review_id':parent(_publication_database),'request_key':uuid4().hex}
    assert client.post('/admin/api/studio/suggestions',json=body).status_code==401
    headers={'Authorization':'Bearer test-admin'}
    job_id=client.post('/admin/api/studio/suggestions',json=body,headers=headers).json()['id']
    assistance.process_next()
    assert client.get('/admin/api/studio/suggestions/'+job_id,headers=headers).json()['status']=='completed'
    normal_id=assistance.enqueue(INTAKE,uuid4().hex)
    assert suggestions.get(normal_id) is None
    with pytest.raises(ValueError,match='fresh AI review'):
        suggestions.enqueue(job_id,None,uuid4().hex)
    draft={'question':QUESTION,'answer':ORIGINAL,'author_name':'CDC reviewer','source_kind':'admin_authored',
           'document_title':'Registration','authority_label':'CDC','department':'all','programs':['internship'],
           'representative_question':QUESTION,'paraphrase_question':'What is the registration credit requirement?',
           'expected_evidence':'1-credit','change_reason':'Verify suggestion isolation.'}
    response=client.post('/admin/api/studio/drafts',headers=headers,json={'review_id':job_id,'draft':draft})
    assert response.status_code==409 and 'fresh review' in response.json()['detail']
