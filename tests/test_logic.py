from app.logic import MAX_TITLE_LENGTH, is_valid_title, normalize_title


def test_normalize_title_trims_and_capitalizes():
    assert normalize_title("  écrire   un workflow ") == "Écrire un workflow"


def test_normalize_title_empty():
    assert normalize_title("   ") == ""


def test_is_valid_title_accepts_normal_title():
    assert is_valid_title("Faire le TP1") is True


def test_is_valid_title_rejects_empty():
    assert is_valid_title("") is False


def test_is_valid_title_rejects_too_long():
    assert is_valid_title("a" * (MAX_TITLE_LENGTH + 1)) is False
