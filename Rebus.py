import requests
import random
from functools import lru_cache
from urllib.parse import quote
import base64
from utils import split_word_via_api, is_letter_char, safe_upper

PIXABAY_API_KEY = "54943820-a53421ed3f0ad1976a3133a66"
PIXABAY_URL = "https://pixabay.com/api/"
DATAMUSE_URL = "https://api.datamuse.com/words"

def generate_svg_data_uri(text: str) -> str:
    """Generates an SVG image as a data URI containing the given text."""
    # Escape simple XML characters just in case
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300">
  <rect width="100%" height="100%" fill="#e0e0e0"/>
  <text x="50%" y="50%" dominant-baseline="central" text-anchor="middle" font-size="120" font-family="sans-serif" fill="#333333">{text}</text>
</svg>'''
    encoded = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{encoded}"

# A pool of common, visualizable nouns for high-quality English Rebus puzzles
COMMON_VISUAL_NOUNS = [
    "APPLE", "ANT", "AXE", "ARM", "BALL", "BAT", "BED", "BEE", "BOAT", "BOX", "BOY", "BUS",
    "CAT", "CAR", "CUP", "CAKE", "CAN", "CAP", "COW", "CORN", "DOG", "DOLL", "DOOR", "DOT",
    "DUCK", "DESK", "DRUM", "EGG", "EAR", "EYE", "ELF", "ELK", "FISH", "FAN", "FOX", "FLY",
    "FORK", "FROG", "GUM", "GOAT", "GAP", "GATE", "GEM", "GUN", "HAT", "HEN", "HIP", "HOG",
    "HOT", "HOP", "HUT", "HAND", "ICE", "INK", "INN", "IVY", "JAR", "JAM", "JET", "JOG",
    "JOY", "JUG", "KEY", "KID", "KIT", "KEG", "LOG", "LID", "LIP", "LEG", "LAB", "MAP",
    "MUD", "MUG", "MOM", "MAT", "MEN", "MIX", "MOON", "NET", "NUT", "NAP", "NOSE", "OWL",
    "OAK", "OIL", "OLD", "ORE", "OX", "PEN", "PIG", "PIN", "POT", "PAN", "PET", "PIE",
    "PIT", "POP", "PUG", "QUEEN", "QUILT", "QUIZ", "RAT", "RED", "RIB", "RIM", "ROD",
    "ROT", "RUG", "RUN", "RAIN", "SUN", "SKY", "SIX", "SOX", "SOY", "SPY", "STY",
    "STAR", "SHIP", "TEN", "TIN", "TIP", "TOP", "TOY", "TUB", "TUG", "TREE", "TENT",
    "UNIT", "URN", "VAN", "VET", "VEX", "VASE", "WEB", "WET", "WIG", "WIN", "WIT",
    "WOLF", "XRAY", "YAK", "YAM", "YEN", "YES", "YET", "YON", "YOYO", "ZOO", "ZAP",
    "ZIP", "ANKLE", "BANANA", "CHAIR", "ELEPHANT", "FLOWER", "GIRAFFE", "HAMMER", "IGLOO",
    "KANGAROO", "LEMON", "MONKEY", "NEST", "ORANGE", "PENCIL", "QUART", "RABBIT", "SNAKE",
    "TIGER", "UMBRELLA", "VIOLIN", "WHALE", "XYLOPHONE", "YACHT", "ZEBRA"
]


@lru_cache(maxsize=1000)
def fetch_clue_words_from_api(char: str, position: int) -> list:
    """Finds common, visualizable nouns with char at 0-indexed position (English only)."""
    pattern = "?" * position + char + "*"
    try:
        response = requests.get(DATAMUSE_URL, params={
            "sp": pattern,
            "max": 100,
            "topics": "object,animal,food,nature,tool,vehicle,clothing",
            "md": "pf"
        }, timeout=3)
        if response.status_code == 200:
            results = response.json()
            nouns = []
            for item in results:
                if "tags" in item and "n" in item["tags"]:
                    freq = 0
                    for tag in item["tags"]:
                        if tag.startswith("f:"):
                            freq = float(tag[2:])
                            break
                    nouns.append((item["word"], freq))

            nouns.sort(key=lambda x: x[1], reverse=True)
            words = [n[0] for n in nouns if " " not in n[0]]
            return [w for w in words if 3 <= len(w) <= 9]
    except Exception:
        pass
    return []


@lru_cache(maxsize=1000)
def fetch_image_from_pixabay(word: str) -> str:
    """Fetches a single image URL for a word from Pixabay."""
    try:
        response = requests.get(PIXABAY_URL, params={
            "key": PIXABAY_API_KEY,
            "q": word,
            "image_type": "photo",
            "per_page": 3,
            "safesearch": "true"
        }, timeout=3)
        if response.status_code == 200:
            hits = response.json().get("hits", [])
            if hits:
                return hits[0]["webformatURL"]
    except Exception:
        pass
    
    return generate_svg_data_uri(word.upper() if word.isascii() else word)


def _reserve_unique_word(candidates: list, used_clues: set):
    """Pick the first available clue word that has not been used yet."""
    random.shuffle(candidates)
    for clue_word, pos in candidates:
        key = clue_word.upper() if clue_word.isascii() else clue_word
        if key not in used_clues:
            used_clues.add(key)
            return safe_upper(clue_word), pos
    return None, None


def _next_fallback_word(char: str, used_clues: set, state: dict) -> str:
    """Generates a guaranteed-unique fallback clue word."""
    while True:
        state["fallback_counter"] += 1
        fallback = f"{safe_upper(char)}{state['fallback_counter']}"
        if fallback not in used_clues:
            used_clues.add(fallback)
            return fallback


def get_puzzle_piece_english(char: str, position_in_target: int, used_clues: set, state: dict):
    """Generates a single puzzle piece for an English character."""
    char_lower = char.lower()

    # Try common nouns pool first
    common_candidates = []
    for word in COMMON_VISUAL_NOUNS:
        word_lower = word.lower()
        for p in [0, 1, 2]:
            if p < len(word_lower) and word_lower[p] == char_lower:
                common_candidates.append((word.upper(), p + 1))

    clue_word, char_pos_in_clue = _reserve_unique_word(common_candidates, used_clues)
    if clue_word:
        img_url = fetch_image_from_pixabay(clue_word)
        return {
            "image_url": img_url,
            "clue_word": clue_word,
            "hint": f"({char_pos_in_clue}/{len(clue_word)})",
            "target_char": char.upper()
        }

    # Fallback to Datamuse API
    possible_pos = [0, 1, 2]
    random.shuffle(possible_pos)
    api_candidates = []
    for p in possible_pos:
        words = fetch_clue_words_from_api(char_lower, p)
        if words:
            random.shuffle(words)
            for w in words:
                if " " not in w:
                    api_candidates.append((w.upper(), p + 1))

    clue_word, char_pos_in_clue = _reserve_unique_word(api_candidates, used_clues)
    if clue_word:
        img_url = fetch_image_from_pixabay(clue_word)
        return {
            "image_url": img_url,
            "clue_word": clue_word,
            "hint": f"({char_pos_in_clue}/{len(clue_word)})",
            "target_char": char.upper()
        }

    # Last resort fallback
    state["fallback_counter"] += 1
    placeholder_text = char if not char.isascii() else f"?{state['fallback_counter']}"
    return {
        "image_url": generate_svg_data_uri(placeholder_text),
        "clue_word": f"?{state['fallback_counter']}",
        "hint": "?",
        "target_char": safe_upper(char)
    }


def get_puzzle_piece_telugu(char: str, char_index: int, total_chars: int, used_clues: set, state: dict):
    """
    Generates a puzzle piece for a Telugu character.
    Since Datamuse/common nouns don't work for Telugu, we use the character itself
    with a position hint and a placeholder image.
    If the character is already used, falls back to a question mark image.
    """
    key = char.upper() if char.isascii() else char
    if key not in used_clues:
        used_clues.add(key)
        # Try fetching an image from Pixabay using the Telugu character as query
        img_url = fetch_image_from_pixabay(char)
        hint = f"({char_index + 1}/{total_chars})"

        return {
            "image_url": img_url,
            "clue_word": char,
            "hint": hint,
            "target_char": char
        }
    else:
        state["fallback_counter"] += 1
        placeholder_text = char if not char.isascii() else f"?{state['fallback_counter']}"
        return {
            "image_url": generate_svg_data_uri(placeholder_text),
            "clue_word": f"?{state['fallback_counter']}",
            "hint": "?",
            "target_char": char
        }


def get_puzzle_piece(char: str, position_in_target: int, total_chars: int = 0,
                     used_clues: set = None, state: dict = None, language: str = "English"):
    """Generates a single puzzle piece for a character."""
    if used_clues is None:
        used_clues = set()
    if state is None:
        state = {"fallback_counter": 0}

    if language == "Telugu":
        return get_puzzle_piece_telugu(char, position_in_target, total_chars, used_clues, state)
    else:
        return get_puzzle_piece_english(char, position_in_target, used_clues, state)


def generate_rebus_puzzle(word: str, preferences: dict = None, used_clues: set = None, state: dict = None) -> dict:
    """Generates a full Rebus puzzle for a word."""
    if preferences is None:
        preferences = {}
    if used_clues is None:
        used_clues = set()
    if state is None:
        state = {"fallback_counter": 0}

    language = preferences.get("language", "English")

    # Split word into logical characters
    if language == "Telugu":
        chars = split_word_via_api(word.strip(), language)
        chars = [ch for ch in chars if is_letter_char(ch)]
    else:
        clean_word = "".join(ch for ch in word.strip() if ch.isalnum())
        chars = list(clean_word)

    total_chars = len(chars)
    pieces = [
        get_puzzle_piece(char, i, total_chars, used_clues, state, language)
        for i, char in enumerate(chars)
    ]

    display_word = "".join(chars)

    return {
        "word": display_word,
        "total_length": total_chars,
        "pieces": pieces,
        "show_solution": preferences.get("show_solution", False),
        "language": language
    }


def generate_puzzles_from_word(word: str, count: int, preferences: dict,
                               used_clues: set = None, state: dict = None) -> list:
    """Generates multiple puzzles for a single word."""
    if used_clues is None:
        used_clues = set()
    if state is None:
        state = {"fallback_counter": 0}

    count = max(1, int(count))
    return [
        generate_rebus_puzzle(word, preferences, used_clues, state)
        for _ in range(count)
    ]


def generate_puzzles_from_words(words: list, count: int, preferences: dict) -> list:
    """Generates puzzles for many words while enforcing global no-repeat clue words."""
    used_clues = set()
    state = {"fallback_counter": 0}
    all_puzzles = []

    for raw_word in words:
        word = raw_word.strip()
        if not word:
            continue
        all_puzzles.extend(
            generate_puzzles_from_word(word, count, preferences, used_clues, state)
        )

    return all_puzzles