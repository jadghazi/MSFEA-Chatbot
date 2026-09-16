"""Git-exported workflow contract; live import is rehearsed separately."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from msfea_bot.curation.validation import REQUIRED_STEPS

_WORKFLOW = Path(__file__).resolve().parents[1] / "n8n" / "workflows" / "kb-publication-guard.json"


def _nodes() -> tuple[dict[str, Any], dict[str, Any]]:
    workflow = json.loads(_WORKFLOW.read_text(encoding="utf-8"))
    return workflow, {node["name"]: node for node in workflow["nodes"]}


def test_workflow_has_two_protected_private_branches() -> None:
    workflow, nodes = _nodes()
    assert workflow["name"] == "KB Publication Guard"
    assert workflow["active"] is True
    assert {node["parameters"]["path"] for node in nodes.values()
            if node["type"] == "n8n-nodes-base.webhook"} == {
                "kb-validation", "kb-publication"
            }
    assert len([node for node in nodes.values()
                if node["type"] == "n8n-nodes-base.if"]) == 2
    for gate in ("Verify Validation Secret", "Verify Publication Secret"):
        condition = nodes[gate]["parameters"]["conditions"]["conditions"][0]
        assert condition["leftValue"] == "={{ $json.headers['x-webhook-secret'] }}"
        assert condition["rightValue"] == "={{ $env.N8N_WEBHOOK_SECRET }}"
        assert condition["operator"] == {"type": "string", "operation": "equals"}
        assert workflow["connections"][gate]["main"][1] == []


def test_workflow_sequences_exact_python_owned_checks_and_intent() -> None:
    workflow, nodes = _nodes()
    http_nodes = [node for node in nodes.values()
                  if node["type"] == "n8n-nodes-base.httpRequest"]
    assert len(http_nodes) == len(REQUIRED_STEPS) + 1
    assert all(node["parameters"]["url"].startswith(
        "http://curation-worker:8001/internal/"
    ) for node in http_nodes)
    assert all(node["maxTries"] == 3 for node in http_nodes)
    for node in http_nodes:
        headers = {item["name"]: item["value"]
                   for item in node["parameters"]["headerParameters"]["parameters"]}
        assert headers["X-Curation-Worker-Token"] == "={{ $env.CURATION_WORKER_TOKEN }}"
        assert "X-Idempotency-Key" in headers
        assert "X-Workflow-Execution-Id" in headers

    first = workflow["connections"]["Verify Validation Secret"]["main"][0][0]["node"]
    order = [first]
    while order[-1] in workflow["connections"]:
        order.append(workflow["connections"][order[-1]]["main"][0][0]["node"])
    bodies = [nodes[name]["parameters"]["body"] for name in order]
    assert len(order) == len(REQUIRED_STEPS)
    assert [re.search(r"step: '([^']+)'", body).group(1) for body in bodies] == list(
        REQUIRED_STEPS
    )
    publication = nodes["Execute Authorized Publication"]
    assert publication["parameters"]["url"].endswith("/publication/execute")
    assert "attempt_id" in publication["parameters"]["body"]
    assert "revision_id" not in publication["parameters"]["body"]
    assert all(node["type"] in {
        "n8n-nodes-base.webhook", "n8n-nodes-base.if", "n8n-nodes-base.httpRequest"
    } for node in nodes.values())
