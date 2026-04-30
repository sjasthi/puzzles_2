from flask import Flask, render_template, jsonify, request
from Grid import Grid
from DropQuote import DropQuote
from Rebus import generate_puzzles_from_words
from quotes_manager import load_quotes, add_quote, remove_quote, replace_quote
from utils import get_fillers_via_api, is_telugu
import base64

app = Flask(__name__)


@app.template_filter('b64encode')
def b64encode_filter(s):
    return base64.b64encode(s.encode()).decode()


# ── Dashboard ──────────────────────────────────────────────

@app.route('/')
def dashboard():
    return render_template("dashboard.html")


# ── Load / Manage Quotes ──────────────────────────────────

@app.route('/load-quotes')
def load_quotes_page():
    quotes = load_quotes()
    return render_template("load_quotes.html", quotes=quotes)


@app.route("/quotes/add", methods=["POST"])
def add():
    data = request.get_json() or {}
    quote = (data.get("quote") or "").strip()
    if not quote:
        return jsonify({"error": "Quote cannot be empty"}), 400
    add_quote(quote)
    return jsonify({"message": "Quote added", "quote": quote})


@app.route("/quotes/remove", methods=["POST"])
def remove():
    data = request.get_json() or {}
    try:
        index = int(data.get("index"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid index"}), 400
    remove_quote(index)
    return jsonify({"message": "Quote removed", "index": index})


@app.route("/quotes/replace", methods=["POST"])
def replace():
    data = request.get_json() or {}
    try:
        index = int(data.get("index"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid index"}), 400
    new_text = (data.get("quote") or "").strip()
    if not new_text:
        return jsonify({"error": "Replacement quote cannot be empty"}), 400
    replace_quote(index, new_text)
    return jsonify({"message": "Quote replaced", "index": index, "new": new_text})


# ── Snakes Puzzle ─────────────────────────────────────────

@app.route('/snakes', methods=['GET', 'POST'])
def snakes():
    all_quotes = load_quotes()

    grid_size_val = request.values.get("grid_size", "10")
    show_solution_val = request.values.get("show_solution")
    puzzle_count_val = request.values.get("puzzle_count", "1")
    language_val = request.values.get("language", "English")

    preferences = {
        "grid_size": int(grid_size_val) if grid_size_val.isdigit() else 10,
        "show_solution": (show_solution_val == "on" or show_solution_val == "true"),
        "puzzle_count": int(puzzle_count_val) if puzzle_count_val.isdigit() else 1,
        "language": language_val,
    }

    # Filter quotes by language
    if preferences["language"] == "Telugu":
        filtered_quotes = [q for q in all_quotes if is_telugu(q)]
    else:
        filtered_quotes = [q for q in all_quotes if not is_telugu(q)]

    selected_quotes = filtered_quotes[:preferences["puzzle_count"]]

    # Fetch fillers in batches of 100
    total_cells = preferences["grid_size"] * preferences["grid_size"]
    total_needed = total_cells * len(selected_quotes)
    fillers = []
    if total_needed > 0:
        for i in range(0, total_needed, 100):
            batch_count = min(100, total_needed - i)
            batch = get_fillers_via_api(preferences["language"], batch_count)
            fillers.extend(batch)

    all_puzzles = []
    filler_start = 0
    for q in selected_quotes:
        puzzle_fillers = fillers[filler_start: filler_start + total_cells]
        filler_start += total_cells
        puzzle = Grid(q, size=preferences["grid_size"], language=preferences["language"], fillers=puzzle_fillers)
        all_puzzles.append({
            "quote": q,
            "grid": puzzle.grid
        })

    return render_template("snakes.html", all_puzzles=all_puzzles, preferences=preferences)


# ── DropQuote Puzzle ──────────────────────────────────────

@app.route('/dropquote', methods=['GET', 'POST'])
def dropquote():
    all_quotes = load_quotes()

    # Support both GET and POST parameters
    show_solution_val = request.values.get("show_solution")
    puzzle_count_val = request.values.get("puzzle_count", "5")
    language_val = request.values.get("language", "English")

    preferences = {
        "show_solution": (show_solution_val == "on" or show_solution_val == "true"),
        "puzzle_count": int(puzzle_count_val) if puzzle_count_val.isdigit() else 5,
        "language": language_val,
    }

    # Filter quotes by language
    if preferences["language"] == "Telugu":
        filtered_quotes = [q for q in all_quotes if is_telugu(q)]
    else:
        filtered_quotes = [q for q in all_quotes if not is_telugu(q)]

    selected_quotes = filtered_quotes[:preferences["puzzle_count"]]

    all_puzzles = []
    for q in selected_quotes:
        dq = DropQuote(q, language=preferences["language"])
        rows = dq.split_quote()
        columns = dq.columns
        max_col_height = max(len(c) for c in columns) if any(columns) else 0

        all_puzzles.append({
            "quote": q,
            "rows": rows,
            "columns": columns,
            "max_col_height": max_col_height
        })

    return render_template("dropquote.html", all_puzzles=all_puzzles, preferences=preferences)


# ── Rebus Puzzle ──────────────────────────────────────────

@app.route('/rebus', methods=['GET', 'POST'])
def rebus():
    if request.method == 'POST':
        puzzle_count = int(request.form.get("puzzle_count", 10))
        show_solution = request.form.get("show_solution") == "on"
        language = request.form.get("language", "English")
    else:
        puzzle_count = 1
        show_solution = False
        language = "English"

    preferences = {
        "puzzle_count": puzzle_count,
        "show_solution": show_solution,
        "language": language,
    }

    all_puzzles = []

    if request.method == 'POST':
        words_raw = request.form.get("words", "")
        words = [w.strip() for w in words_raw.splitlines() if w.strip()]
        if words:
            all_puzzles = generate_puzzles_from_words(
                words,
                preferences["puzzle_count"],
                preferences
            )

    return render_template("rebus.html", all_puzzles=all_puzzles, preferences=preferences)


if __name__ == '__main__':
    app.run(debug=True)
