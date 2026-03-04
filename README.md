# DataMind

DataMind is a data analysis assistant. You upload a dataset, ask questions in natural language, and get answers as text, tables, or charts.

The project has:
- A FastAPI backend for dataset ingestion, cleaning, query interpretation, analytics, and chart data generation.
- A React frontend for chat-driven analysis, dataset preview, and graph rendering.

## Why DataMind
DataMind is designed for users who want fast insights from tabular data without writing SQL or pandas code manually.

Typical flow:
1. Upload a CSV/Excel/JSON dataset.
2. Ask chat questions in natural language.
3. View scalar answers as readable text, grouped/ranked results as tables, and visualization results as charts.

## Key Features
1. Dataset upload and preprocessing
- Supports `.csv`, `.xlsx`, `.xls`, `.json`.
- Runs a cleaning pipeline after upload.
- Stores active dataset in in-memory backend datastore for chat and graph routes.

2. Natural language analytics
- Detects intents: analytics, filter, group-by, visualization.
- Supports natural-language filtering and conditions.

3. Group-by analytics
- Supports grouped analytics from natural-language input and returns tabular output.

4. Rank/slice queries
- Supports ranking and slicing style queries from chat input.
- Multi-row results are returned as table payloads.

5. Smart response formatting
- Single-value analytics answers are returned as readable text.
- Multi-value results are returned as structured tables.
- Visualization requests are returned as chart payloads.

6. Graph generation API
- Separate graph endpoints for interactive frontend plotting.
- Supports `histogram`, `bar`, `pie`, `line`, `scatter`.

7. Dataset viewer
- Paginated dataset preview endpoint.
- Datetime values are normalized to `YYYY-MM-DD` for cleaner display.
- Missing values are made JSON-safe.

## Tech Stack
Backend:
- Python 3.14+
- FastAPI
- Pandas, NumPy, scikit-learn
- Uvicorn

Frontend:
- React 19 + Vite
- React Router
- Tailwind CSS
- Recharts

## Project Structure
```text
DataMind/
  Backend/
    core/
      data_cleaner.py
      data_loader.py
      outlier_detector.py
      pipeline_manager.py
    ml/
      intent_detector.py
      query_engine.py
      visualization_engine.py
    routes/
      upload_router.py
      chat_router.py
      graph_router.py
      dataset_router.py
    services/
      chat_service.py
    main.py
    pyproject.toml
  Frontend/
    src/
      components/
        ChatWindow.jsx
        MessageBubble.jsx
        DataTable.jsx
        DatasetPage.jsx
        GraphPage.jsx
        FileUpload.jsx
        ChartRenderer.jsx
      App.jsx
```

## Setup and Run
### 1) Backend
From `Backend/`:

```bash
# Create venv (optional if you already have one)
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Install dependencies
pip install -e .

# Run API server
python -m uvicorn main:app --reload
```

Backend runs at `http://127.0.0.1:8000` by default.

### 2) Frontend
From `Frontend/`:

```bash
npm install
npm run dev
```

Frontend typically runs at `http://127.0.0.1:5173`.
