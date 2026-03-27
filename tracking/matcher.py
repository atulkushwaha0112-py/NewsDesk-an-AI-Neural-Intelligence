"""
tracking/matcher.py
────────────────────
Precise news matching for the tracking system.

Uses a multi-signal approach:
1. Extract KEY entities from the title (proper nouns, important terms)
2. Build bigrams for phrase matching (e.g., "Delhi airport", "West Asia")
3. Score articles with weighted matching:
   - Title-to-title matches score MUCH higher than title-to-description
   - Bigram (phrase) matches score higher than single-word matches
   - Require at least 50% of key terms to match in the title
"""
import re
from news_reader import _load_category, _news_id, _parse_time, _clean
from config import ALL_CATEGORIES


# Expanded stop words — common words that don't help identify a topic
_STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "may", "might", "can", "could", "of", "in", "to", "for",
    "with", "on", "at", "from", "by", "about", "as", "into", "through",
    "during", "before", "after", "above", "below", "between", "out", "off",
    "over", "under", "again", "further", "then", "once", "and", "but", "or",
    "nor", "not", "no", "so", "if", "that", "this", "these", "those",
    "it", "its", "he", "she", "they", "them", "his", "her", "their",
    "what", "which", "who", "whom", "how", "when", "where", "why",
    "all", "each", "every", "some", "any", "few", "more", "most", "other",
    "up", "down", "just", "now", "also", "very", "much", "too", "than",
    "amid", "says", "set", "check", "per", "new", "news", "two",
    "likely", "near", "next", "rise", "year", "years", "time", "times",
    "get", "got", "make", "made", "take", "give", "gives", "additional",
    "here", "there", "back", "top", "first", "last", "many", "such",
    "come", "like", "well", "day", "days", "week", "weeks", "month",
    "key", "big", "way", "use", "look", "long", "think",
}


def _extract_key_terms(title: str) -> list[str]:
    """Extract important keywords from a title, filtering out noise."""
    words = re.findall(r"[a-zA-Z]{3,}", title)
    # Keep words that are:
    # 1. Not stop words
    # 2. Capitalized (proper nouns) get priority, but lowercase content words are kept too
    terms = []
    for w in words:
        lower = w.lower()
        if lower not in _STOP_WORDS:
            terms.append(lower)
    return list(dict.fromkeys(terms))  # deduplicate, preserve order


def _extract_bigrams(title: str) -> list[str]:
    """Extract consecutive word pairs from a title for phrase matching."""
    words = re.findall(r"[a-zA-Z]{3,}", title.lower())
    words = [w for w in words if w not in _STOP_WORDS]
    bigrams = []
    for i in range(len(words) - 1):
        bigrams.append(f"{words[i]} {words[i+1]}")
    return bigrams


def _score_article(target_terms: list[str], target_bigrams: list[str],
                    article: dict) -> float:
    """
    Score how relevant an article is to the target terms.

    Scoring:
    - Each keyword found in the article TITLE = 3 points
    - Each keyword found in description only = 0.5 points (much lower)
    - Each bigram found in article TITLE = 5 points (phrase match is strong)
    - Each bigram found in description = 1 point

    Returns 0 if below relevance threshold.
    """
    art_title = article.get("title", "").lower()
    art_desc = (article.get("short_desc", "") + " " + article.get("long_desc", "")).lower()

    score = 0.0
    title_hits = 0

    # Single keyword matching
    for term in target_terms:
        if term in art_title:
            score += 3.0
            title_hits += 1
        elif term in art_desc:
            score += 0.5

    # Bigram matching (phrase matching — much more precise)
    for bg in target_bigrams:
        if bg in art_title:
            score += 5.0
            title_hits += 1
        elif bg in art_desc:
            score += 1.0

    # THRESHOLD: Need at least 40% of key terms to appear in the title
    if len(target_terms) > 0:
        title_coverage = title_hits / len(target_terms)
        if title_coverage < 0.35:
            return 0.0

    # Need a minimum score to be considered related
    min_score = max(6.0, len(target_terms) * 1.5)
    if score < min_score:
        return 0.0

    return round(score, 1)


def find_related_news(title: str, limit: int = 50) -> list[dict]:
    """Find news articles precisely related to a title."""
    terms = _extract_key_terms(title)
    bigrams = _extract_bigrams(title)

    if not terms:
        return []

    results = []
    seen = set()

    for cat in ALL_CATEGORIES:
        for a in _load_category(cat):
            nid = _news_id(a)
            if nid in seen:
                continue
            seen.add(nid)

            score = _score_article(terms, bigrams, a)
            if score > 0:
                a["news_id"] = nid
                a["_score"] = score
                a["_pub_dt"] = _parse_time(a.get("published_time", ""))
                results.append(a)

    # Sort by score (best match first), then by time
    results.sort(
        key=lambda a: (a["_score"], a["_pub_dt"].timestamp() if a.get("_pub_dt") else 0),
        reverse=True,
    )

    return [
        _clean(a) | {"match_score": a.get("_score", 0)}
        for a in results[:limit]
    ]
