# BizPilot

**Your AI co-pilot for turning raw ideas into thriving businesses.**

BizPilot is a Django web application that helps entrepreneurs go from a rough idea to a launched, growing business through intelligent automation. It pairs a friendly chat interface with a **multi-agent AI system** that delivers business plans, market research, financial guidance, launch roadmaps, sales forecasts, and document/image analysis, all personalized and step-by-step.

---

## Features at a Glance

| Capability | What it does |
|---|---|
| **Multi-Agent AI Chat** | A coordinated team of specialist AI agents answers business questions and routes each query to the right expert. |
| **Business Planning** | Generates comprehensive, investor-ready business plans (executive summary, market analysis, business model, financials). |
| **Market Research** | Live competitive and market analysis using real-time web search. |
| **Financial Advisory** | Pricing strategy, funding options, revenue models, and projections, backed by live financial data. |
| **Roadmap Generation** | Detailed, time-bound launch roadmaps with monthly milestones and KPIs. |
| **Sales Forecasting** | Time-series forecasting (Facebook Prophet) from your CSV sales data, with scenario analysis. |
| **Business Recommendations** | Turns forecasts into actionable advice on inventory, production, hiring, and cash flow. |
| **OCR Image Analysis** | Extracts and analyzes text from business cards, receipts, invoices, charts, and screenshots. |
| **Document Analysis** | Reads and summarizes uploaded PDF, Word, TXT, and Excel/CSV files. |
| **Chart Generation** | Produces Chart.js-ready visualizations (bar, line, pie) on request. |
| **Eco-Friendly Advisor** | Sustainability-focused guidance for green and circular-economy businesses. |
| **User Accounts** | Login/logout with a protected chatbot workspace. |

---

## How the AI Works

BizPilot is built around a **coordinator + specialists** architecture using the [phidata](https://github.com/phidatahq/phidata) agent framework. A master **Coordinator** agent manages a team of focused specialists, and incoming messages are automatically routed to the best-suited agent based on keywords and intent.

### The Agent Team

| Agent | Specialty |
|---|---|
| **BizPilot Coordinator** | Orchestrates the team and synthesizes multi-agent answers for complex queries. |
| **Business Planner** | Comprehensive startup business plans and strategy. |
| **Market Researcher** | Market sizing, trends, and competitor analysis (via DuckDuckGo web search). |
| **Financial Advisor** | Pricing, funding, and projections (via Yahoo Finance data). |
| **Roadmap Generator** | Time-bound launch roadmaps and milestones. |
| **Sales Forecasting Agent** | Prophet-based forecasting plus operational recommendations. |
| **OCR Text Analyzer** | Business insights from text extracted out of images. |
| **File Analyzer** | Analysis of uploaded documents. |
| **Chart Generator** | Structured chart data for visualizations. |
| **Eco-Friendly Advisor** | Sustainable and green business guidance. |

### Smart Routing

Queries are matched to specialists by intent, for example:

- *"Help me write a business plan..."* goes to the **Business Planner**
- *"Who are the competitors in...?"* goes to the **Market Researcher**
- *"How should I price my SaaS?"* goes to the **Financial Advisor**
- *"Give me a 6-month roadmap..."* goes to the **Roadmap Generator**
- *"Forecast my sales for 30 days"* (with CSV) goes to the **Sales Forecasting Agent**
- *"Analyze this receipt"* (with image) goes to the **OCR Text Analyzer**
- Anything broad or multi-faceted goes to the **Coordinator** (uses the whole team)

### Flexible Models and Graceful Fallbacks

- Works with **OpenAI (GPT-4o)** or **Groq (Llama 3.3 70B)**, swappable via a single flag.
- If AI models are unavailable (missing API keys, network issues), BizPilot automatically falls back to helpful **static responses**, so the app never breaks.

---

## Tech Stack

- **Backend:** Django 5.2 (Python)
- **AI/Agents:** phidata, OpenAI, Groq
- **Tools:** DuckDuckGo Search, Yahoo Finance (yfinance)
- **Forecasting:** Facebook Prophet, pandas, NumPy
- **OCR:** pytesseract, Pillow, OpenCV
- **Documents:** PyPDF2, python-docx, openpyxl, pandas
- **Database:** MySQL (XAMPP-friendly) via PyMySQL; SQLite also supported
- **Frontend:** Django templates, vanilla JS, Chart.js

---

## Project Structure

```
BizPilot/
├── landingpage.html              # Standalone marketing landing page
├── bizpilot.sql                  # MySQL database dump
├── assets/                       # Landing page images
└── server/                       # Django project
    ├── manage.py
    ├── requirements.txt
    ├── setup_bizpilot.py         # One-command dependency installer & checker
    ├── .env                      # API keys (OPENAI_API_KEY, GROQ_API_KEY)
    ├── core/                     # Django settings, URLs, WSGI/ASGI
    ├── main/                     # Pages: home, login/logout, chatbot
    ├── chat/                     # Chat & file-upload API endpoints
    ├── bizpilot_agents.py        # Multi-agent AI system (the brain)
    ├── forecasting_tools.py      # Prophet forecasting + business recommendations
    ├── ocr_tools.py              # OCR text extraction & analysis
    ├── templates/                # index, login, chatbot pages
    ├── static/                   # CSS, images
    └── sample_*.csv              # Sample sales data for testing forecasts
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- (Optional) MySQL via XAMPP, or use SQLite
- (Optional) [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) for real image OCR (a mock mode runs without it)

### 1. Clone and enter the project

```bash
git clone <your-repo-url>
cd BizPilot
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows (PowerShell)
./venv/Scripts/Activate.ps1
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r server/requirements.txt
```

> You can also run `python server/setup_bizpilot.py` (from inside `server/`) to install core packages and verify the setup interactively.

### 4. Configure API keys

Create or edit `server/.env`:

```env
OPENAI_API_KEY=sk-your-openai-key-here
GROQ_API_KEY=gsk_your-groq-key-here
```

- Get an OpenAI key: https://platform.openai.com/api-keys
- Get a free Groq key: https://console.groq.com/keys

> By default BizPilot uses **Groq (free)**. If no keys are set, it falls back to static responses.

### 5. Set up the database and run

```bash
cd server
python manage.py migrate
python manage.py runserver
```

Then open **http://127.0.0.1:8000/**

> **Database note:** Settings are pre-configured for MySQL (XAMPP defaults: database `bizpilot`, user `root`, empty password). Import `bizpilot.sql` via phpMyAdmin, or switch the `DATABASES` setting in `server/core/settings.py` to SQLite for a zero-config start.

---

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/chat/` | Send a chat message; returns an AI (or static) reply. Body: `{ "message": "..." }` |
| `POST` | `/api/upload/` | Upload a file (CSV/PDF/DOCX/TXT/image) for analysis or forecasting. |
| `POST` | `/api/idea/` | Submit a business idea for ingestion. |
| `GET`  | `/api/pricing/` | Retrieve subscription pricing tiers. |
| `POST` | `/api/feedback/` | Submit user feedback. |

**Pages:** `/` (home), `/login/`, `/logout/`, `/chatbot/` (login-required), `/admin/`

---

## Try It Out

Once running, sign in and try prompts like:

**Business planning**
> "Help me create a business plan for a sustainable fashion brand targeting Gen Z."

**Market research**
> "What's the market size and main competitors for AI fitness apps?"

**Financial planning**
> "How should I price my project-management SaaS?"

**Roadmaps**
> "Create a 6-month launch roadmap for my online store."

**Sales forecasting** (upload `sample_sales_data.csv`)
> "Forecast sales for the next 30 days and show optimistic, realistic, and pessimistic scenarios."

**Business recommendations** (upload a CSV)
> "Provide comprehensive business recommendations. Inventory: 800, price: $25, cost: $12, salary: $400."

**Charts**
> "Show me a bar chart comparing projected revenue across the first 6 months."

**OCR** (upload an image)
> "Analyze this business card and extract the contact information."

---

## Sales Forecasting Details

The forecasting engine (`forecasting_tools.py`) uses **Facebook Prophet** to turn historical CSV sales data into forward-looking predictions, and layers intelligent business advice on top:

- **Flexible CSV parsing:** auto-detects date and sales columns (multi-language keyword support, with type-based fallbacks).
- **Scenario analysis:** optimistic, realistic, and pessimistic projections.
- **Confidence intervals:** upper/lower bounds for each predicted day.
- **Comprehensive recommendations:** inventory restock alerts, production volumes (with safety buffers), staffing needs, and revenue/cost/profit projections.
- **Custom parameters:** specify `inventory`, `price`, `cost`, `salary`, and forecast `days` directly in your message.

> See [`ENHANCED-FORECASTING.md`](ENHANCED-FORECASTING.md) for the full forecasting reference.

---

## OCR Image Analysis Details

The OCR module (`ocr_tools.py`) extracts text from images and analyzes it for business value:

- **Formats:** JPG, JPEG, PNG, GIF, BMP, TIFF, WEBP
- **Image preprocessing** with OpenCV for better accuracy
- **Structured extraction:** emails, phone numbers, dates, currency values, percentages, company names
- **Quality scoring and confidence** reporting
- **Mock mode** so the pipeline works even before Tesseract is installed

> See [`OCR-IMPLEMENTATION.md`](OCR-IMPLEMENTATION.md) for details and [`README-AI-AGENTS.md`](README-AI-AGENTS.md) for the agent system.

---

## Roadmap / Future Enhancements

- Custom agent training on your own business data
- Integrations with CRM/ERP/analytics tools
- Multi-language and voice interaction
- Automated alerts (email/SMS) for critical forecast thresholds
- Real-time team collaboration

---

## Notes

- The included `SECRET_KEY`, open CORS, and `DEBUG=True` are **development defaults**. Change them before deploying to production.
- API keys belong in `.env` and should never be committed to source control.

---

## License

No license file is currently included. Add one (e.g. MIT) to clarify usage and contribution terms.

---

<p align="center"><i>BizPilot: from idea to launch, with AI at the helm.</i></p>
