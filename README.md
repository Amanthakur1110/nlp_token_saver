# TokenSaver

A web demo for comparing NLP token-compression techniques.  
Upload a PDF, DOCX, TXT, or MD file, pick one or more techniques, and see how many tokens are saved and how well the meaning is preserved.

---

## How to run

```bash
cp .env.example .env          # add ANTHROPIC_API_KEY if you want abstractive_llm
docker compose up --build
```

Then open **http://localhost:5173** in your browser.

- Backend API: http://localhost:5000/api/health
- Docker Compose waits for the backend health check before starting the frontend, so its initial API requests do not race backend startup.
- Results show each selected technique's independent output once, plus the final combined-chain output, with removed text highlighted in red.
- First build pulls ~2 GB of Python packages + spaCy model.
- First request that uses sentence-transformers downloads ~400 MB (cached in `hf_cache` volume).
- First LLMLingua-2 use downloads ~700 MB (also cached).

---

## Architecture

```
frontend (Vite + React + Tailwind)  :5173
        |  POST /api/upload
        |  GET  /api/techniques
        |  POST /api/compress
        v
backend (Flask)  :5000
  ├── pipeline/
  │     extractor.py   → raw text from file
  │     cleaner.py     → unicode normalisation
  │     runner.py      → apply techniques, record per-step data
  │     metrics.py     → token counts, similarity, ROUGE-L, …
  │     diff.py        → kept/removed word and punctuation segments
  │     report.py      → assemble JSON response
  └── techniques/
        (one folder per technique, auto-discovered by registry.py)
```

---

## How to add a new technique

1. Create `backend/techniques/my_technique/technique.py`.
2. Write ONE class that extends `BaseTechnique`.
3. Set `id`, `name`, `description`, `params_schema` as class attributes.
4. Implement `apply(self, text, params) -> str`.
5. Optionally override `is_available()` if your technique has optional dependencies.
6. Create `backend/techniques/my_technique/README.md` following the standard template.
7. Rebuild Docker: `docker compose up --build`.

That's it — `registry.py` auto-discovers the new folder.

---

## Known limitations

- **No database.** Uploaded documents are stored in memory on the server. Restarting Docker loses them.
- **LLMLingua-2** requires ~700 MB download on first use and works best on meeting transcripts.
- **Abstractive LLM** requires an Anthropic API key and consumes your API quota.
- **sentence-transformers** model (~400 MB) is downloaded on first use by `extractive_summary` or `semantic_dedup`.
- The diff view highlights removed words and phrases in the original text.
- The backend is single-process Flask dev server — fine for a demo, not for production.
- spaCy model is English only; `grammar_based` and entity metrics will be poor on other languages.

---

## Project structure

```
tokensaver/
├── docker-compose.yml
├── .env.example
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py            Flask factory + health endpoint
│   ├── config.py         all settings
│   ├── routes/           upload, techniques, compress
│   ├── pipeline/         extractor → cleaner → runner → metrics → diff → report
│   ├── techniques/       one folder per technique
│   ├── utils/            tokenizer (tiktoken), nlp_models (lazy singletons)
│   └── tests/            pytest tests, one per technique
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx
        ├── api.js
        └── components/   UploadPanel, TechniquePicker, ResultsTable, DiffView, MetricsPanel
```
