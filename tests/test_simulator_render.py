from app.core.models import PageDefinition, Severity, WidgetData
from app.render.layout_engine import LayoutEngine
from app.render.simulator import SimulatorRenderer


def test_simulator_renders_frame() -> None:
    engine = LayoutEngine(128, 32)
    page = PageDefinition(page_id="p1", name="Test", layout="single_kpi", widgets=["clock"])
    data = {
        "clock": WidgetData(
            widget_id="clock",
            title="Clock",
            value="12:00:00",
            severity=Severity.ok,
            source_label="test",
        )
    }
    image = engine.render_page(page, data)
    renderer = SimulatorRenderer(128, 32)
    renderer.draw_frame(image)
    out = renderer.get_last_image()
    assert out.size == (128, 32)
