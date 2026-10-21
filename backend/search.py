import re, unicodedata

STOP = {"comment", "faire", "pour", "les", "des", "une", "que", "qui", "quoi", "dans", "son", "ses",
        "mon", "mes", "ton", "tes", "est", "sur", "avec", "bien", "quel", "quelle", "quels", "quelles",
        "peut", "etre", "ainsi", "tout", "tous", "vous", "votre", "conseillez", "quelqu", "francs",
        "fcfa", "cherche", "chercher", "veut", "veux", "voudrais", "aimerais", "mais", "plus", "moins",
        "aussi", "comme", "entre", "sans", "sous", "par", "the", "how", "and", "for", "with", "what",
        "can", "you", "want", "need", "creation", "creer", "cree"}

def norm(text):
    return unicodedata.normalize("NFKD", str(text or "").lower()).encode("ascii", "ignore").decode()

def keywords(text):
    """Important words of a question, cut to 5 letters so that economiser matches economie."""
    return [w[:5] for w in re.findall(r"[a-z0-9]+", norm(text))
            if len(w) >= 3 and w not in STOP and not w.isdigit()]

def score(words, title, *others):
    title = norm(title)
    rest = norm(" ".join(str(o or "") for o in others))
    return sum((2 if w in title else 0) + (1 if w in rest else 0) for w in words)