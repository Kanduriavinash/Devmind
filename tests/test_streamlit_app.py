from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_streamlit_homepage_renders_without_an_error():
    app_path = Path(__file__).resolve().parents[1] / "streamlit_app.py"
    app = AppTest.from_file(app_path, default_timeout=15).run()
    assert app.title[0].value == "DevMind"
    assert len(app.text_input) == 3
    assert len(app.text_area) == 1
    assert any(button.label == "Analyze repository" for button in app.button)
    app_source = app_path.read_text(encoding="utf-8")
    assert '[data-testid="stFormSubmitButton"] button:hover:not(:disabled)' in app_source
    assert "transform: translateY(-2px) scale(1.015)" in app_source
    assert not app.exception


def test_dashboard_handles_stats_without_candidate_metric(monkeypatch):
    from devmind import stats

    monkeypatch.setattr(
        stats,
        "compute_dashboard_stats",
        lambda records: {
            "total_runs": 0,
            "unique_projects": 0,
            "test_pass_rate": None,
            "patches_generated": 0,
            "projects": {},
            "status_distribution": {},
        },
    )
    app_path = Path(__file__).resolve().parents[1] / "streamlit_app.py"

    app = AppTest.from_file(app_path, default_timeout=15).run()

    assert not app.exception


def test_app_uses_local_galaxy_assets_without_a_user_color_picker():
    import streamlit as st

    app_path = Path(__file__).resolve().parents[1] / "streamlit_app.py"
    app = AppTest.from_file(app_path, default_timeout=15).run()

    assert not app.exception
    assert not app.get("color_picker")
    assert st.get_option("server.enableStaticServing") is True
    assert (app_path.parent / "static" / "galaxy.mp4").is_file()
    assert (app_path.parent / "static" / "galaxy-poster.jpg").is_file()
    app_source = app_path.read_text(encoding="utf-8")
    assert '<video class="devmind-galaxy"' in app_source
    assert "devmind-bug" not in app_source


def test_repository_source_switch_immediately_changes_input_to_github_url():
    app_path = Path(__file__).resolve().parents[1] / "streamlit_app.py"
    app = AppTest.from_file(app_path, default_timeout=15).run()

    assert app.text_input[0].label == "Repository folder"
    app.segmented_control[0].set_value("Public GitHub URL").run(timeout=15)

    assert app.text_input[0].label == "Public GitHub repository URL"
    assert not app.exception


def test_demo_preset_selection_populates_repo_and_bug_description():
    app_path = Path(__file__).resolve().parents[1] / "streamlit_app.py"
    app = AppTest.from_file(app_path, default_timeout=15).run()

    # Initial state is custom entry
    assert app.text_input[0].value == ""
    assert app.text_area[0].value == ""

    # Selecting Cricket Scorer preset populates repository path and bug description
    app.selectbox[0].select("Cricket scorer · JavaScript ball-count bug").run(timeout=15)
    assert "cricket-scorer" in app.text_input[0].value
    assert "matchState.balls += 1" in app.text_area[0].value
    assert not app.exception

    # Selecting Safe Divide preset populates buggy_project and division bug description
    app.selectbox[0].select("Safe divide · Python zero-division bug").run(timeout=15)
    assert "buggy_project" in app.text_input[0].value
    assert "safe_divide crashes" in app.text_area[0].value
    assert not app.exception

    # Selecting Custom Bug resets or allows manual entry
    app.selectbox[0].select("Custom Bug (Manual Entry)").run(timeout=15)
    assert app.text_input[0].value == ""
    assert app.text_area[0].value == ""
    assert not app.exception

