"""Admin content curation (ADR-0010).

Lets authorized CDC staff answer questions the bot couldn't (unanswered /
thumbs-down) from the admin dashboard. The answer is stored in Postgres and
becomes a retrievable KB chunk — closing the loop so the bot can answer it next
time, grounded and cited. This is content authoring (not model training).
"""
