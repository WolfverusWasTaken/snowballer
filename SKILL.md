---
name: snowballer
description: Research a topic by following primary sources backward and forward, save one source-linked idea per folder, and build or browse a searchable graph of multiple reports. Use for literature maps, past-work surveys, model and software-stack comparisons, or updates to an existing Snowballer report.
---

# Snowballer

Turn a user-defined research question into a source-vetted, interconnected idea catalog. The report title, scope, depth, and stopping point come from the user; do not hardcode this skill's example project or a fixed number of ideas.

## Research workflow

1. Read the user's brief and any existing report. State a working project description and revise it as evidence accumulates.
2. Search across relevant disciplines. Read primary papers, documentation, datasets, and repositories before adding an idea. Follow cited predecessors and later work where useful. A bibliographic lead is not a vetted idea.
3. Give each distinct work one `ideas/<id>/` folder with an `idea.json` and technical `README.md`. Explain the method, evidence, limitations, and implications in plain English; include mathematical detail when it clarifies the mechanism. Challenge the user's proposed architecture when the evidence warrants it.
4. Link only verified IDs in `past_work` and `related_work`. Distinguish a direct predecessor from a merely related idea. Use the [schema and evidence rules](references/schema.md) when writing or checking entries.
5. From this skill folder, run `python scripts/snowballer.py build --root <report-folder>` to validate and generate `master.json`. Do not count unreviewed queue entries as ideas.
6. Register a report with `python scripts/snowballer.py register --root <report-folder> --title "<user-facing title>"`. The title is configurable per report. Start the shared browser with `python scripts/server.py`; one server lists every registered report and reads its idea folders on demand.

For a new report, use `python scripts/snowballer.py init --root <report-folder> --title "<user-facing title>"`, then research and build. The user may request a different output structure; adapt while retaining an indexable idea catalog. Stop at the user's requested cap or when the useful source trail is exhausted. Do not pad the count.

## Tooling and output

The helper script is at `scripts/snowballer.py`, relative to this skill folder. The server has `/api/reports`, per-report idea, search, and file routes; its HTML interface is `assets/index.html`. The report directory remains the source of truth. The HTML does not embed every idea or require a separate server per report. Do not copy the sample project's fixed title or logo into unrelated reports; a report can register an optional local logo.

Run the helper's `--help` for commands and use a free local port when 8000 is occupied. Report the actual browser URL and the report folder to the user.
