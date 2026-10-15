# Idea schema and evidence

Each `ideas/<id>/idea.json` contains:

```json
{
  "id": "stable-slug",
  "title": "Work title",
  "year": 2024,
  "kind": "short-method-category",
  "description": "Plain-English summary of the work",
  "what_it_does": "Problem it addresses",
  "pros": ["Evidence-backed strength"],
  "cons": ["Evidence-backed limitation"],
  "tags": ["searchable-general-tag"],
  "novelty": "A ten to fifteen word explanation of the actual contribution",
  "core_discovery": "The finding or useful disagreement",
  "past_work": ["verified-earlier-id"],
  "related_work": ["verified-related-id"],
  "folder_path": "ideas/stable-slug",
  "sources": ["https://primary-source.example/paper"]
}
```

`past_work` should name a verified predecessor, not simply a similar work. Use `related_work` for comparisons without a predecessor claim. Keep sources specific to the claim and prefer the paper, author repository, standards body, or official documentation. Record exact evaluation setup and metrics when available; do not imply that benchmark accuracy proves transfer to the user's setting. The README should explain inputs, outputs, representation, core computation, training or optimization, evaluation, limitations, and project relevance as applicable. Do not invent details that the source does not provide.

The catalog builder checks required fields, IDs, folder paths, novelty length, HTTPS sources, and graph references. It cannot establish whether the research claims are true; read the sources and review the technical notes.
