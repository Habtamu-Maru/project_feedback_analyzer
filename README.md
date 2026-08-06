# 📊 Project Feedback Analyzer

A **Gemini-powered customer feedback analyzer** that reads customer reviews and automatically returns:

- **Label** — `positive`, `negative`, or `neutral`
- **Score** — an integer from `1` (very bad) to `5` (very good)
- **Theme** — a short description of the main topic of the review

The project provides **two ways to use it** — a full **Streamlit web UI** and a lightweight **FastAPI REST endpoint** — so you can choose whichever fits your workflow.

---

## ✨ Features

- 🔍 **Single Review Analysis** — paste one review and get instant sentiment analysis.
- 📦 **Batch Analysis** — analyze many reviews at once (one per line) or load the included sample reviews.
- 📈 **Dashboard** — visual summaries: sentiment distribution, top themes, average score, and score distribution.
- 🗂 **History & Export** — every analysis is recorded in-session and can be downloaded as a **CSV** file.
- 🌐 **REST API** — a simple `POST /analyze` endpoint for programmatic access.

---

## 🗂 Project Structure

```
project_feedback_analyzer/
├── app.py                  # Streamlit web UI (main entry point)
├── api.py                  # FastAPI REST endpoint
├── analyzer.py             # Reusable Gemini analysis logic (used by the UI)
├── sample_review.txt       # 10 sample reviews for testing
├── pyproject.toml          # Project config & dependencies (managed by uv)
├── uv.lock                 # Locked dependency versions
├── .env                    # Your Google Gemini API key (NOT committed)
└── src/project_feedback_analyzer/
    └── __init__.py         # Package entry point
```

> **Note:** `app.py` imports `analyzer` directly, so the Streamlit app runs **self-contained** without needing the FastAPI server.

---

## ✅ Prerequisites

- **Python 3.10 or higher**
- **`uv`** — fast Python package & project manager ([install guide](https://docs.astral.sh/uv/getting-started/installation/))
- A **Google Gemini API key** from [Google AI Studio](https://aistudio.google.com/)

---

## 🚀 Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd project_feedback_analyzer
```

### 2. Create your environment file

Create a `.env` file in the project root and add your API key:

```bash
# .env
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY_HERE
```

> `.env` is already in `.gitignore`, so your key will never be committed.

### 3. Install dependencies

Using **uv** (recommended):

```bash
uv sync
```

Or with plain `pip`:

```bash
pip install -e .
```

---

## ▶️ Running the Streamlit Web UI

```bash
uv run streamlit run app.py
```

Or without uv:

```bash
streamlit run app.py
```

Then open the URL shown in the terminal (usually `http://localhost:8501`).

### Using the UI

1. **Analyze Review** — type a review and click **Analyze**.
2. **Batch Analysis** — paste multiple reviews (one per line) or click **Load sample reviews**, then **Analyze batch**.
3. **Dashboard** — view aggregated charts and metrics for everything analyzed in this session.
4. **History & Export** — review all results and **Download results as CSV**.

---

## ▶️ Running the FastAPI REST API

In a separate terminal:

```bash
uv run uvicorn api:app --reload
```

The interactive API docs will be available at **http://localhost:8000/docs**.

### Example request

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "The delivery was quick and the food arrived hot."}'
```

### Example response

```json
{
  "label": "positive",
  "score": 5,
  "theme": "delivery speed"
}
```

---

## 🧪 Sample Data

The file `sample_review.txt` contains **10 example reviews** covering positive, negative, and neutral sentiments. You can load them directly in the **Batch Analysis** page to try the tool quickly.

---

## ⚙️ Configuration

- **Gemini model** — the model name is set to `gemini-3.5-flash` in **`analyzer.py`** and **`api.py`**. Update the `MODEL` / `model` variable there to use a different Gemini model.
- **API key** — read automatically from the `.env` file via `python-dotenv`.

---

## 🔧 Troubleshooting

| Problem | Solution |
| --- | --- |
| `Analysis failed` / missing key error | Ensure `.env` exists and contains a valid `GOOGLE_API_KEY`. |
| `Could not find sample_review.txt` | Run the app from the `project_feedback_analyzer` directory (or create the file). |
| Port already in use | Use a different port, e.g. `streamlit run app.py --server.port 8502`. |
| Import errors | Make sure dependencies are installed (`uv sync` or `pip install -e .`). |

---

## 📄 License

This project is for educational/demo purposes. You may adapt it freely.

---

## 👤 Author

**Habtamu Amru** — [habtamumaruu@gmail.com](mailto:habtamumaruu@gmail.com)
