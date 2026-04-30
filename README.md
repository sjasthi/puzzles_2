# 🐍 Snakes — A Multi-Lingual Puzzle Generator

A Flask-based web application that generates three types of puzzles — **Snakes**, **Drop Quote**, and **Rebus** — with full support for **English** and **Telugu** languages.

---

## ✨ Features

### 🐍 Snakes Puzzle
- Hide a quote as a continuous winding path through a grid of letters
- Configurable grid size (10×10 to 20×20)
- Language-specific filler characters via the [Ananya API](https://jasthi.com/ananya/)
- Highlight solution path toggle

### ⬇️ Drop Quote Puzzle
- Classic [Drop Quote](https://en.wikipedia.org/wiki/Dropquote) puzzle generator
- Shuffled letter columns drop into a blank answer grid to form a quote
- Supports up to 100 puzzles per generation
- Full Unicode support for Telugu characters

### 🧩 Rebus Puzzle
- Generate visual word puzzles with image clues from [Pixabay](https://pixabay.com/)
- Each letter of the target word is clued by a picture + positional hint
- English: Uses a curated pool of visual nouns + [Datamuse API](https://www.datamuse.com/api/) fallback
- Telugu: Uses Ananya API for logical character splitting with Pixabay image search
- Scale to **100 puzzles per word** input
- Interactive answer checking with auto-advance

### 🌍 Multi-Language Support
- **English** and **Telugu** languages for all puzzle types
- Language selector in every puzzle sidebar
- Ananya API integration for correct Telugu logical character parsing
- Unicode-aware character handling throughout

### 📄 Quote Management
- Add, remove, and replace quotes via the web interface
- Quotes stored in `quotes.txt` (one per line)
- Automatic language detection (Telugu vs English) for filtering

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd snakes

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate    # Linux/Mac
# venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Open your browser to **http://127.0.0.1:5000**

---

## 📂 Project Structure

```
snakes/
├── app.py                 # Flask application — all routes
├── quotes_manager.py      # Quote CRUD operations (load, add, remove, replace)
├── Grid.py                # Snakes puzzle grid generation with backtracking
├── Cell.py                # Grid cell data model
├── DropQuote.py           # Drop Quote puzzle logic
├── Rebus.py               # Rebus puzzle generation (Pixabay + Datamuse APIs)
├── utils.py               # Shared utilities (Ananya API, Unicode helpers)
├── quotes.txt             # Quote database (English + Telugu)
├── requirements.txt       # Python dependencies
├── static/
│   ├── style.css          # Global stylesheet
│   └── js/
│       └── script.js      # Client-side scripts
├── templates/
│   ├── layout.html        # Base template (navbar, Bootstrap 5, Google Fonts)
│   ├── dashboard.html     # Home page — puzzle selector cards
│   ├── snakes.html        # Snakes puzzle UI
│   ├── dropquote.html     # Drop Quote puzzle UI
│   ├── rebus.html         # Rebus puzzle UI (interactive)
│   └── load_quotes.html   # Quote management page
└── assets/
    ├── how_to_call_api.txt
    └── quotes_1.txt       # Additional quote source
```

---

## 🔧 Configuration

All puzzle settings are configurable via the web interface sidebar:

| Setting | Default | Range | Puzzles |
|---|---|---|---|
| Grid Size | 10 | 10–20 | Snakes |
| Puzzle Count | 1–5 | 1–100 | All |
| Language | English | English / Telugu | All |
| Show Solution | Off | On / Off | All |

**Bookmarkable URLs**: Snakes and Drop Quote use GET parameters so settings are preserved in the URL.

---

## 🌐 API Dependencies

### Ananya API (Telugu Support)
- **Character Splitting**: `https://jasthi.com/ananya/api.php/characters/logical`
- **Filler Characters**: `https://jasthi.com/ananya/api.php/characters/filler`
- Used for parsing Telugu text into logical characters (handling complex clusters like `న్య`)

### Pixabay API (Rebus Images)
- **Endpoint**: `https://pixabay.com/api/`
- Free tier: 100 requests/minute
- Used to fetch photo clues for Rebus puzzle words
- **Cost**: Free (no upgrade needed). Pixabay provides generous free access with attribution.

### Datamuse API (Rebus Word Clues)
- **Endpoint**: `https://api.datamuse.com/words`
- Free and unlimited
- Used as a fallback to find English nouns matching specific letter patterns

### Image API Cost Comparison (FP9.5)

| Provider | Free Tier | Cost to Upgrade | Quality |
|---|---|---|---|
| **Pixabay** (current) | 100 req/min, unlimited | Free forever | ✅ High-quality photos |
| Flickr | 3600 req/hr | Free API key | Good, varied |
| Hugging Face (AI) | Limited inference | ~$9/month Pro | AI-generated, slower |

**Decision**: Pixabay was chosen as the primary image source — it's free, high quality, and has excellent coverage for common English nouns used in Rebus puzzles. No paid upgrade is needed.

---

## 🖨️ Printing

Every puzzle page includes a **Print** button that generates a clean PDF:
- Sidebar and navigation are hidden
- Each puzzle gets its own page
- Colors are preserved with `print-color-adjust`

---

## 📜 License

See [LICENSE](LICENSE) for details.
