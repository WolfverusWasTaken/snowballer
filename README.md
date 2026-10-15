# Snowballer

Snowballer is a Codex skill for building source-linked research maps. It follows relevant work backward through references and forward through later research, saves one vetted idea per folder, and serves searchable graphs for multiple reports from one local server.

The report title, topic, stopping point, and optional logo belong to each report. Research data stays outside this skill repository.

## What it produces

```text
my-report/
├── README.md              # brief and evolving synthesis
├── ideas/
│   └── example-idea/
│       ├── idea.json       # metadata and graph links
│       └── README.md       # technical notes and critique
└── master.json             # validated catalog generated from idea folders
```

Each idea records its sources, contribution, strengths, limitations, tags, predecessors, and related work. The [schema](references/schema.md) describes the fields and evidence rules.

## Use as a Codex skill

Place or link this folder at `~/.codex/skills/snowballer`, then invoke `$snowballer` in Codex. For example:

> Use `$snowballer` to map research on my topic. Save vetted ideas in a new report and show me the graph.

The [skill instructions](SKILL.md) guide source review and catalog updates. There is no fixed idea count or baked-in report title.

## Command-line tools

From this repository root, with Python 3.10 or newer:

```text
python scripts/snowballer.py init --root PATH --title "My research map"
python scripts/snowballer.py build --root PATH
python scripts/snowballer.py register --root PATH --title "My research map"
python scripts/snowballer.py list
python scripts/server.py --port 8000
```

`init` creates and registers a new report folder. `register` adds an existing report; pass `--logo PATH` to give it a local image. `build` validates the idea folders and refreshes `master.json`. Open `http://localhost:8000/` after starting the server. Its report selector lets you switch between registered reports. Search and idea details are read from the selected report directory; the HTML does not embed the full catalog.

The server binds to `127.0.0.1`. It offers `/api/reports`, `/api/reports/<id>/ideas`, `/api/reports/<id>/ideas/<idea-id>`, and `/api/reports/<id>/search?q=...&year=...&tag=...`. Registration state is stored at `~/.codex/snowballer/reports.json` or the path in `SNOWBALLER_REGISTRY`.
