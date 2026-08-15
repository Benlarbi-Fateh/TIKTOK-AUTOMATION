from scripts.source_manager import SourceManager


def test_get_active_sources():
    manager = SourceManager()
    sources = manager.get_active_sources()
    assert isinstance(sources, list)
