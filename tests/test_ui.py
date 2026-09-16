import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
os.environ["LLM_PROVIDER"] = "mock"

from streamlit.testing.v1 import AppTest


def test_streamlit_app_renders_without_exception():
    app = AppTest.from_file("app/streamlit_app.py", default_timeout=20).run()

    assert not app.exception
    assert any(button.label == "Analyse before submitting" for button in app.button)
    assert any(text_input.label == "Short summary" for text_input in app.text_input)

    next(item for item in app.text_input if item.label == "Short summary").set_value(
        "Operations dashboard revenue differs from Finance"
    )
    next(item for item in app.text_area if item.label == "Describe the problem").set_value(
        "Executive Sales dashboard expected EUR 1.91M but displays EUR 1.82M for France month-to-date."
    )
    next(item for item in app.text_input if item.label == "Your name or work email").set_value(
        "employee@company.com"
    )
    app = next(button for button in app.button if button.label == "Analyse before submitting").click().run()

    assert not app.exception
    assert any("A similar request was solved" in item.value for item in app.markdown)
    assert any("Data &amp; Analytics Team" in item.value or "Data & Analytics Team" in item.value for item in app.markdown)
    assert any(button.label == "Submit ticket to recommended team" for button in app.button)

    view_selector = next(radio for radio in app.radio if radio.label == "Choose your view")
    app = view_selector.set_value("Support Workspace").run()

    assert not app.exception
    assert len(app.tabs) == 4
    assert len(app.text_area) == 1
    assert any(button.label == "Approve draft" for button in app.button)
    create_button = next(button for button in app.button if button.label == "+ Create ticket")

    app = create_button.click().run()

    assert not app.exception
    assert any(text_input.label == "Short summary" for text_input in app.text_input)
    assert any(button.label == "Create and run agents" for button in app.button)
