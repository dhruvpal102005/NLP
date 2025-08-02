import requests
import json
import sys

g_api = 'https://inputtools.google.com/request?text={}&itc={}-t-i0-und&num={}'
qp_api = 'http://xlit.quillpad.in/quillpad_backend2/processWordJSON?lang={}&inString={}'

lang2code = {
    "hindi": "hi", "tamil": "ta", "telugu": "te", "marathi": "mr",
    "punjabi": "pa", "bengali": "bn", "gujarati": "gu", 
    "kannada": "kn", "malayalam": "ml", "nepali": "ne"
}

def gtransliterate(word, lang_code, num_suggestions=10):
    url = g_api.format(word, lang_code, num_suggestions)
    response = requests.get(url, allow_redirects=False, timeout=5)

    try:
        r = json.loads(response.text)
        if response.status_code != 200 or r[0] != "SUCCESS":
            print(f"Request failed with status code: {response.status_code}\nERROR: {response.text}", file=sys.stderr)
            return []
        return r[1][0][1]
    except Exception as e:
        print(f"Exception occurred: {e}", file=sys.stderr)
        return []

def qp_transliterate(word, lang):
    url = qp_api.format(lang, word)
    response = requests.get(url, allow_redirects=False, timeout=5)
    
    if response.status_code != 200 or "Internal Server Error" in response.text:
        print(f"Request failed with status code: {response.status_code}\nERROR: {response.text}", file=sys.stderr)
        return []

    try:
        r = json.loads(response.text)
        suggestions = r.get("twords", [{}])[0].get("options", [])
        suggestions.append(r.get("itrans", ""))
        return suggestions
    except Exception as e:
        print(f"Failed to parse response: {e}", file=sys.stderr)
        return []

def transliterate(word, lang, source):
    if "quill" in source:
        return qp_transliterate(word, lang)
    elif "google" in source:
        return gtransliterate(word, lang2code.get(lang, ""))
    else:
        sys.exit(f"ERROR: Source {source} not found")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(f"USAGE: python {sys.argv[0]} <eng_word> <supported_lang>")

    word, lang = sys.argv[1], sys.argv[2]
    
    if not word or lang not in lang2code:
        sys.exit(f"USAGE: python {sys.argv[0]} <eng_word> <supported_lang>")

    print("QUILLPAD suggestions:\n{}\n".format(transliterate(word, lang, 'quillpad')))
    print(" GOOGLE  suggestions:\n{}\n".format(transliterate(word, lang, 'google')))
