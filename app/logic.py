"""Logique métier de l'application (fonctions pures, faciles à tester)."""

MAX_TITLE_LENGTH = 80


def normalize_title(title: str) -> str:
    """Supprime les espaces en trop et met la première lettre en majuscule."""
    cleaned = " ".join(title.split())
    if not cleaned:
        return ""
    return cleaned[0].upper() + cleaned[1:]


def is_valid_title(title: str) -> bool:
    """Un titre est valide s'il n'est pas vide et ne dépasse pas MAX_TITLE_LENGTH."""
    cleaned = normalize_title(title)
    return 0 < len(cleaned) <= MAX_TITLE_LENGTH
