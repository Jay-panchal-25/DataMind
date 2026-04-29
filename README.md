# DataMind

DataMind is an AI-powered data analysis tool with built-in AutoML capabilities. It lets users upload tabular data, explore cleaned records, ask natural-language questions, generate charts, and run lightweight machine-learning predictions from the same workspace.

## Highlights

- Upload datasets in `CSV`, `Excel`, or `JSON` format.
- Run an automatic cleaning pipeline after upload.
- Preview the processed dataset with pagination.
- Ask data analysis questions in natural language.
- View answers as text, tables, charts, or prediction cards.
- Run AutoML-based predictions from user-provided feature values.
- Keep short conversational memory across recent chat turns.

## Tech Stack

### Backend

- Python 3.14+
- FastAPI
- Pandas
- NumPy
- scikit-learn
- Matplotlib
- Google GenAI client support for LLM-based planning and summarization

### Frontend

- React
- Vite
- Axios
- Tailwind CSS utilities

## Architecture

### Backend

The backend is responsible for:

- loading uploaded files
- cleaning and normalizing datasets
- building dataset reports and warnings
- translating chat prompts into executable plans
- running analytics, chart generation, and AutoML predictions
- returning JSON-safe responses to the frontend


### Frontend

The frontend provides:

- upload and workspace flow
- dataset overview and preview screens
- chat-driven analysis UI
- prediction and chart rendering components

## Project Structure

```text
DataMind/
|- Backend/
|  |- core/
|  |- ml/
|  |- routes/
|  |- services/
|  |- main.py
|  `- pyproject.toml
|- Frontend/
|  |- src/
|  |  |- components/
|  |  |- services/
|  |  `- App.jsx
|  `- package.json
`- README.md
```

## Features in Detail

### 1. Dataset Upload and Cleaning

After upload, DataMind:

- validates the file type
- loads the dataset into a Pandas DataFrame
- removes duplicate rows
- applies data cleaning utilities
- performs outlier correction for numeric fields
- builds a report with overview metrics and warnings

### 2. Natural-Language Analytics

Users can ask questions such as:

- `show max and min salary by department`
- `find average age by team`
- `list rows where rating is 5`

The planner converts prompts into structured execution steps, then the execution layer returns either a short text answer or a table payload.

### 3. Visualizations

Chart prompts are converted into backend-generated chart images. Supported chart types include:

- `bar`
- `line`
- `scatter`
- `histogram`
- `pie`

### 4. Predictions

Prediction prompts can estimate a target column from feature values, for example:

- `predict salary when department is engineering age is 35 experience is 7 rating is 4`

The backend includes a lightweight AutoML flow that trains candidate models on the active dataset and returns:

- selected model name
- task type
- evaluation metrics
- predicted output
- input values
- feature importance payload


## Local Setup

### 1. Backend

From the `Backend` directory:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
python -m uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`.

### Optional environment configuration

If you want LLM-assisted planning and summaries, create a `.env` file inside `Backend/` and provide a Gemini API key:

```env
GEMINI_API_KEY=your_key_here
```

Without it, the app falls back to rule-based planning for supported prompts.

### 2. Frontend

From the `Frontend` directory:

```bash
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

## Typical Workflow

1. Start the backend.
2. Start the frontend.
3. Upload a dataset.
4. Open the dataset viewer or chat workspace.
5. Ask for summaries, grouped metrics, charts, filters, or predictions.
