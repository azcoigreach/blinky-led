from app.core.models import PageDefinition
from app.pages.rotation import RotationController


def test_pinned_page_override() -> None:
    pages = [
        PageDefinition(page_id="a", name="A", layout="single_kpi"),
        PageDefinition(page_id="b", name="B", layout="single_kpi"),
    ]
    rot = RotationController(pages)
    assert rot.current("b").page_id == "b"
