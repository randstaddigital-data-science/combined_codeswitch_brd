from pygments.lexers import guess_lexer, get_all_lexers
from langdetect import detect
import langid

# mapping of lexer names
LEXER_MAPPING = {"Python": "Python", "Java": "Java", "Cpp": "C++", "Cobol": "COBOL"}


def detect_language(code):
    try:
        lexer = guess_lexer(code)
        if lexer.name in LEXER_MAPPING:
            return LEXER_MAPPING[lexer.name]
    except Exception as e:
        print(f"Pygments detection failed: {e}")

    try:
        lang = detect(code)
        if lang == "en":
            return refine_language_detection(code)
    except Exception as e:
        print(f"Langdetect detection failed: {e}")

    try:
        langid.set_languages(["en"])
        lang, _ = langid.classify(code)
        if lang == "en":
            return refine_language_detection(code)
    except Exception as e:
        print(f"Langid detection failed: {e}")

    return "Unknown"


def refine_language_detection(code):
    # additional heuristic patterns
    if "def " in code or "import " in code:
        return "Python"
    elif "#include" in code or "int main" in code:
        return "C++"
    elif "public static void main" in code or "import java." in code:
        return "Java"
    elif "IDENTIFICATION DIVISION" in code:
        return "COBOL"
    return "Unknown"
