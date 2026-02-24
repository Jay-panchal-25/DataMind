# DataMind

DataMind is a data analysis assistant that lets you upload a dataset, ask questions in plain language, and generate charts from your data. The backend is a FastAPI service for file ingestion, analytics, and chart data; the frontend is a React + Vite app that provides the chat and visualization UI.

**Features**

1. Upload CSV/Excel datasets and keep them in a simple in-memory store.
2. Ask natural-language questions for basic analytics.
3. Generate charts (histogram, bar, pie, line, scatter) from selected columns.
4. Paginated dataset preview with JSON-safe values.

**Tech Stack**

1. Backend: Python 3.14, FastAPI, Pandas, NumPy, scikit-learn, Uvicorn.
2. Frontend: React 19, Vite 7, React Router, Recharts, Tailwind CSS.

**Project Structure**

```text
DataMind/
  Backend/
    core/
      data_cleaner.py
      data_loader.py
      outlier_detector.py
      pipeline_manager.py
    ml/
      imputers.py
      intent_detector.py
      query_engine.py
      visualization_engine.py
    routes/
      chat_router.py
      dataset_router.py
      graph_router.py
      upload_router.py
    services/
      chat_service.py
    main.py
    pyproject.toml
    uv.lock
    .python-version
  Frontend/
    public/
      logo.png
      vite.svg
    src/
      components/
        ChartRenderer.jsx
        ChatInput.jsx
        ChatWindow.jsx
        DatasetPage.jsx
        FileUpload.jsx
        GraphPage.jsx
        MessageBubble.jsx
        Sidebar.jsx
      App.jsx
      index.css
      main.jsx
    package.json
    vite.config.js
    index.html
```

**Setup**
Backend: from `Backend/`, install dependencies with your preferred Python environment tool. Start the API server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Frontend: from `Frontend/`, install and run:

```bash
npm install
npm run dev
```

**API Endpoints**

1. `POST /upload` � Multipart file upload that stores the dataset in memory and returns column names and row count.
2. `POST /chat` � Body: `{ "message": "..." }`. Returns either text analytics or chart data based on intent detection.
3. `GET /columns` � Returns dataset column names for chart configuration.
4. `POST /generate-graph` � Body: `{ "chart_type": "bar|pie|line|scatter|histogram", "x": "...", "y": "..." }`. Returns chart payload ready for the frontend.
5. `GET /dataset?page=1&page_size=10` � Returns paginated rows and column metadata.
