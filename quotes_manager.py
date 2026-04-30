"""
Manages loading, adding, removing, and replacing quotes in quotes.txt.
"""
import os

QUOTES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'quotes.txt')


def load_quotes(filepath=None) -> list:
    """Read quotes from a text file (one quote per line) and return a list."""
    if filepath is None:
        filepath = QUOTES_FILE
    quotes = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    quotes.append(line)
    except FileNotFoundError:
        pass
    return quotes


def _rewrite_file(quotes, filepath=None):
    """Overwrite quotes.txt with the given list of quotes."""
    if filepath is None:
        filepath = QUOTES_FILE
    with open(filepath, 'w', encoding='utf-8') as f:
        for quote in quotes:
            f.write(f'{quote}\n')


def add_quote(quote: str, filepath=None):
    """Append a quote to the file."""
    quotes = load_quotes(filepath)
    quotes.append(quote)
    _rewrite_file(quotes, filepath)


def remove_quote(index: int, filepath=None):
    """Remove a quote by 1-based index."""
    quotes = load_quotes(filepath)
    if 1 <= index <= len(quotes):
        del quotes[index - 1]
        _rewrite_file(quotes, filepath)


def replace_quote(index: int, new_text: str, filepath=None):
    """Replace a quote at a 1-based index."""
    quotes = load_quotes(filepath)
    if 1 <= index <= len(quotes):
        quotes[index - 1] = new_text
        _rewrite_file(quotes, filepath)
