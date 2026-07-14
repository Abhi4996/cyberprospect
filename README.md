# CyberProspect

**Cybersecurity Sales Intelligence Platform**

CyberProspect ingests Shodan network scan data (~70GB JSONL), processes it through a PySpark ETL pipeline, stores aggregated results in DuckDB, and presents an interactive Streamlit dashboard for prospecting and targeting businesses with demonstrated cybersecurity weaknesses. It also features an AI-powered sales pitch generator using Google Gemini.

> For detailed architecture, design decisions, scoring methodology, and schema documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Prerequisites

1. **Python 3.9+**
2. **Java 11+** (required for PySpark)
   - Windows: `winget install Microsoft.OpenJDK.17` or install OpenJDK manually
   - Mac: `brew install openjdk@17`
   - Linux: `sudo apt install openjdk-17-jdk`
3. **Google AI Studio API Key** *(optional, for AI Pitch Generator)* — [Get it here](https://aistudio.google.com/)

---

## Installation & Setup

### Quick Setup (Windows)

```bash
setup.bat
```

### Manual Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/cyberprospect.git
   cd cyberprospect
   ```

2. **Create a virtual environment and install dependencies**:
   ```bash
   python -m venv venv

   # Windows
   .\venv\Scripts\activate

   # Mac/Linux
   source venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Data Preparation**:
   - The repository includes a sample dataset at `input/test_scans_sample.json`.
   - To use the full dataset, place `test_scans.json.zst` (or `.json`) into the `input/` directory and update `INPUT_FILE` in `etl/config.py`.

---

## Running the Application

### Step 1: Run the ETL Pipeline

The ETL pipeline processes the raw JSONL data into Parquet format and computes risk scores.

```bash
# Ensure your virtual environment is activated
python -m etl.run_pipeline
```

This creates processed files in `data/parquet/` and takes ~30–60 minutes on the full dataset.

### Step 2: Launch the Dashboard

```bash
streamlit run app/Overview.py
```

This will open the dashboard in your browser at `http://localhost:8501`.

### Quick Launch (Windows)

```bash
run.bat
```

---

## Application Pages

| Page | Description |
|:---|:---|
| **🏠 Dashboard** | Executive overview with KPI cards, top 10 riskiest orgs chart, and risk score distribution. |
| **🔍 Prospect Finder** | Filter and search organizations by risk score, IP count, and other criteria. |
| **🏢 Company Deep Dive** | Detailed breakdown of a single organization's security posture, exposed infrastructure, and CVEs. |
| **🌍 Geo Map** | Interactive world map visualizing the physical locations of exposed infrastructure. |
| **🤖 AI Pitch Generator** | Generate hyper-personalized sales outreach emails for the top 500 organizations using Gemini. |

---

## Deployment (Free Hosting)

### Recommended: Streamlit Community Cloud

The simplest way to share CyberProspect with others at zero cost.

> **Important:** The deployed app only needs **DuckDB + Streamlit** at runtime. PySpark and Java are only needed for the ETL step, which you run **locally** before deploying.

#### Step-by-Step

1. **Run the ETL pipeline locally** to generate the Parquet files:
   ```bash
   python -m etl.run_pipeline
   ```

2. **Temporarily un-ignore the `data/` directory** so Parquet files get committed.
   Edit `.gitignore` and comment out the `data/` line:
   ```
   # data/    ← comment this out temporarily
   ```

3. **Push the repository to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit with processed data"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/cyberprospect.git
   git push -u origin main
   ```

4. **Go to [share.streamlit.io](https://share.streamlit.io/)** and sign in with your GitHub account.

5. **Click "New app"** and configure:
   - **Repository**: `YOUR_USERNAME/cyberprospect`
   - **Branch**: `main`
   - **Main file path**: `app/Overview.py`

6. **Add secrets** (optional, for AI Pitch Generator):
   - In the Streamlit Cloud dashboard, go to **Settings → Secrets**
   - Add your Gemini API key:
     ```toml
     GEMINI_API_KEY = "your-api-key-here"
     ```

7. **Click "Deploy"** — your app will be live at `https://YOUR_USERNAME.streamlit.app` within a few minutes.

8. **Re-add `data/` to `.gitignore`** after the initial deploy if you don't want to track data in Git long-term.

#### Notes on Streamlit Cloud

- **Memory limit**: 1GB. Your processed Parquet files should be well under this.
- **No PySpark needed**: The app only uses DuckDB to query the pre-processed Parquet files.
- **Automatic redeployment**: Pushes to `main` automatically trigger a redeployment.
- **Custom domain**: Available via Streamlit Cloud settings.

### Alternative: Docker-based Hosts (Render, Railway, Fly.io)

If you need more control, create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app/Overview.py", "--server.port", "8501", "--server.enableCORS", "false"]
```

| Platform | Free Tier | Deploy Command |
|:---|:---|:---|
| **Render** | 750 hrs/month | Connect GitHub repo → Web Service → Dockerfile |
| **Railway** | $5/month credit | `railway up` |
| **Fly.io** | 3 shared VMs | `fly launch` then `fly deploy` |

---

## Project Structure

```
shodan_assignment/
├── ARCHITECTURE.md        # Detailed architecture & design document
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── .gitignore
├── .streamlit/
│   └── config.toml        # Streamlit theme configuration
├── setup.bat              # Windows setup script
├── run.bat                # Windows launch script
│
├── input/                 # Raw Shodan data
│   └── test_scans_sample.json
├── etl/                   # PySpark ETL pipeline
│   ├── config.py          # Paths & excluded orgs
│   ├── schema.py          # Explicit PySpark schemas
│   ├── ingest.py          # Read JSONL
│   ├── transform.py       # Flatten, dedup, explode
│   ├── score.py           # Risk scoring
│   ├── export.py          # Write Parquet
│   └── run_pipeline.py    # Pipeline orchestrator
├── data/                  # Processed output (gitignored)
│   ├── parquet/
│   └── cyberprospect.duckdb
├── app/                   # Streamlit dashboard
│   ├── Overview.py        # Entry point
│   ├── pages/             # Multi-page UI
│   └── utils/             # db.py, llm.py
├── hadoop/                # Windows PySpark binaries
├── tests/                 # Test suite
└── docs/                  # Documentation
```

---

## Troubleshooting

| Problem | Solution |
|:---|:---|
| `java.io.IOException: Cannot run program "java"` | Install Java 11+ and ensure it is in your system PATH. |
| Streamlit Database Error | Run the ETL pipeline first: `python -m etl.run_pipeline` |
| DuckDB lock error | Close DBeaver or any other process that has the `.duckdb` file open. |
| Empty dashboard | Click **🔄 Rebuild Dashboard Cache** in the sidebar, or re-run the ETL pipeline. |
| AI Pitch Generator error | Enter a valid Google AI Studio API key in the sidebar. |

---

## License

This project was created as a technical assessment for a data engineering role.
