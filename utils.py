import random
import string
from urllib.parse import quote

import requests

def split_word_via_api(text: str, language: str = "English") -> list:
    """
    Calls the TeluguPuzzles API to split a string into logical characters.
    """
    try:
        encoded_string = quote(text)
        url = f"https://jasthi.com/ananya/api.php/characters/logical?string={encoded_string}&language={language}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        response = requests.get(url, timeout=5, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("result"):
                return data["result"]
    except Exception:
        pass
    
    # Fallback to standard split if API fails
    return list(text)

def get_fillers_via_api(language: str = "English", count: int = 100) -> list:
    """
    Calls the TeluguPuzzles API to get filler characters.
    """
    try:
        url = f"https://jasthi.com/ananya/api.php/characters/filler?language={language}&count={count}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
        }
        response = requests.get(url, timeout=5, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("result"):
                return data["result"]
    except Exception:
        pass

    # Fallback: Telugu letters or ASCII uppercase
    if language.lower() == "telugu":
        telugu_fillers = [
            "అ", "ఆ", "ఇ", "ఈ", "ఉ", "ఊ", "ఋ", "ఎ", "ఏ", "ఐ", "ఒ", "ఓ", "ఔ",
            "క", "ఖ", "గ", "ఘ", "చ", "ఛ", "జ", "ఝ", "ట", "ఠ", "డ", "ఢ", "ణ",
            "త", "థ", "ద", "ధ", "న", "ప", "ఫ", "బ", "భ", "మ", "య", "ర", "ల",
            "వ", "శ", "ష", "స", "హ", "ళ", "క్ష", "ఱ"
        ]
        return [random.choice(telugu_fillers) for _ in range(count)]
    return [random.choice(string.ascii_uppercase) for _ in range(count)]


def is_letter_char(char: str) -> bool:
    """
    Check if a character is a letter or alphanumeric.
    Works for English (ASCII) and Telugu (Unicode 0C00-0C7F) characters.
    """
    if not char or char == ' ':
        return False
    if char.isalnum():
        return True
    # Telugu Unicode range
    if any('\u0c00' <= c <= '\u0c7f' for c in char):
        return True
    return False


def safe_upper(text: str) -> str:
    """
    Uppercase only if ASCII. Telugu and other scripts have no case, so return as-is.
    """
    if any('\u0c00' <= c <= '\u0c7f' for c in text):
        return text
    return text.upper()


def is_telugu(text: str) -> bool:
    """Check if text contains Telugu characters."""
    return any('\u0c00' <= char <= '\u0c7f' for char in text)
