from unittest.mock import MagicMock, patch, mock_open
from custom_components.enever_prijzen.cache import EneverCache


def test_cache_management_pipeline():
    """Verify JSON persistence layer writes text strings and handles corrupted reads gracefully."""
    hass = MagicMock()
    cache = EneverCache(hass)

    # 1. Test loading from missing files safely returns empty templates
    with patch("os.path.exists", return_value=False):
        assert cache.load_cache() == {"stroom": [], "gas": []}

    # 2. Test reading corrupted structural profiles skips and logs out exceptions
    with (
        patch("os.path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data="NOT_JSON")),
    ):
        assert cache.load_cache() == {"stroom": [], "gas": []}

    # 3. Test writing payloads cleanly triggers save sequences
    with patch("builtins.open", mock_open()) as mock_file:
        cache.save_cache({"test": "data"})
        mock_file.assert_called_once_with(cache.cache_path, "w", encoding="utf-8")

    # 4. Test clearance calls invoke unlink processes directly
    with patch("os.path.exists", return_value=True), patch("os.remove") as mock_remove:
        cache.clear_cache()
        mock_remove.assert_called_once_with(cache.cache_path)
