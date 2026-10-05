#!/usr/bin/env python3
"""Builds books.json: every Penguin Classics title Open Library knows about.
Run on your own machine:  python3 scrape_penguin_classics.py
Then put books.json next to penguin-classics-random.html and serve both."""
import json, time, urllib.parse, urllib.request

BASE = "https://openlibrary.org/search.json"
FIELDS = "key,title,author_name,first_publish_year,cover_i,isbn"

def get(params):
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "penguin-classics-random/1.0 (personal project)"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception:
            time.sleep(2 * (attempt + 1))
    raise SystemExit("Open Library request failed repeatedly; try again later.")

books, seen, page = [], set(), 1
while page <= 80:
    d = get({"q": 'publisher:"Penguin Classics"', "fields": FIELDS, "limit": 100, "page": page})
    docs = d.get("docs", [])
    if not docs:
        break
    for x in docs:
        author = (x.get("author_name") or ["Unknown"])[0]
        sig = (x["title"].lower().strip(), author.lower())
        if sig in seen:
            continue
        seen.add(sig)
        books.append({"key": x["key"], "title": x["title"], "author": author,
                      "year": x.get("first_publish_year"), "cover_i": x.get("cover_i"),
                      "isbn": (x.get("isbn") or [None])[0]})
    print(f"page {page}: {len(books)} unique titles so far")
    page += 1
    time.sleep(1)  # be polite to the API

with open("books.json", "w", encoding="utf-8") as f:
    json.dump(books, f, ensure_ascii=False)
print(f"Wrote books.json with {len(books)} titles")
