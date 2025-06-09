from urllib.parse import quote_plus

STORES = [
    {
        "name": "طاقچه",
        "logo": "taaghche.png",
        "base_url": "https://taaghche.com",
        "search_path": "/search?term=",
        "non_book_only": True,
    },
    {
        "name": "دیجیکالا",
        "logo": "digikala.svg",
        "base_url": "https://digikala.com",
        "search_path": "/search/?q=",
        "non_book_only": False,  # non‐book‐only stores need the extra 'کتاب' term
    },
]

def build_search_url(store: dict, term: str) -> str:
    """
    Append an extra 'کتاب' keyword for non-specialized stores,
    URL-encode the full query, and return the absolute URL.
    """
    # if the store is NOT a specialized bookshop, tack on 'کتاب'
    if not store["non_book_only"]:
        term = 'کتاب ' + term
    # URL‐encode spaces and non-ASCII characters
    encoded = quote_plus(term)
    # construct and return the final URL
    return f"{store['base_url'].rstrip('/')}{store['search_path']}{encoded}"