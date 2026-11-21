import os

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.path.join(BASE_DIR, "user_data")
TRACKING_DIR  = os.path.join(BASE_DIR, "tracking")
NEWS_DATA_DIR = os.path.join(BASE_DIR, "NEWS_DATA_ET")
ADMIN_DATA_DIR = os.path.join(BASE_DIR, "admin", "admin_data")

SECRET_KEY = os.getenv("NEWS_DESK_SECRET_KEY", "").strip()
if not SECRET_KEY:
    raise RuntimeError("NEWS_DESK_SECRET_KEY must be configured in the environment.")
ALGORITHM                   = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL    = "llama3.2:latest"

ALL_CATEGORIES = {
    "top_news":         "Top News",
    "latest_news":      "Latest News",
    "markets":          "Markets",
    "stocks":           "Stocks",
    "ipo":              "IPO",
    "cryptocurrency":   "Cryptocurrency",
    "commodities":      "Commodities",
    "forex":            "Forex",
    "bonds":            "Bonds",
    "india_news":       "India News",
    "economy":          "Economy",
    "politics":         "Politics",
    "international":    "International",
    "company":          "Company",
    "defence":          "Defence",
    "science":          "Science",
    "environment":      "Environment",
    "sports":           "Sports",
    "elections":        "Elections",
    "industry":         "Industry",
    "tech_industry":    "Tech Industry",
    "healthcare":       "Healthcare",
    "services":         "Services",
    "media_ent":        "Media & Entertainment",
    "transportation":   "Transportation",
    "renewables":       "Renewables",
    "banking_finance":  "Banking & Finance",
    "startups":         "Startups",
    "funding":          "Funding",
    "information_tech": "Information Technology",
    "tech_internet":    "Tech & Internet",
    "education":        "Education",
    "wealth":           "Wealth",
    "mutual_funds":     "Mutual Funds",
    "personal_finance": "Personal Finance",
    "insurance":        "Insurance",
    "tax":              "Tax",
    "small_biz":        "Small Business",
    "entrepreneurship": "Entrepreneurship",
    "gst":              "GST",
    "jobs":             "Jobs & Careers",
    "opinion":          "Opinion",
    "et_editorial":     "ET Editorial",
    "travel":           "Travel",
    "et_magazine":      "ET Magazine",
    "nri":              "NRI",
}

CATEGORY_GROUPS = {
    "Top Stories":      ["top_news", "latest_news"],
    "Markets":          ["markets", "stocks", "ipo", "cryptocurrency", "commodities", "forex", "bonds"],
    "News":             ["india_news", "economy", "politics", "international", "company", "defence", "science", "environment", "sports", "elections"],
    "Industry":         ["industry", "tech_industry", "healthcare", "services", "media_ent", "transportation", "renewables", "banking_finance"],
    "Tech & Startups":  ["startups", "funding", "information_tech", "tech_internet", "education"],
    "Personal Finance": ["wealth", "mutual_funds", "personal_finance", "insurance", "tax"],
    "Small Business":   ["small_biz", "entrepreneurship", "gst"],
    "Jobs":             ["jobs"],
    "Opinion":          ["opinion", "et_editorial"],
    "Lifestyle & NRI":  ["travel", "et_magazine", "nri"],
}

os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(TRACKING_DIR,  exist_ok=True)
os.makedirs(ADMIN_DATA_DIR, exist_ok=True)
