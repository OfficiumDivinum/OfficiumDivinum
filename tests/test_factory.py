from officiumdivinum.api import create_app


def test_config():
    """Test that setting testing config works."""
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing
