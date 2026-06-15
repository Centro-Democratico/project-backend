from core.views import _is_admin, _require_admin, _component_to_dict
from unittest.mock import MagicMock


def test_is_admin_returns_true_when_header_valid():
    request = MagicMock()
    request.headers = {'X-User-Admin': 'true'}

    assert _is_admin(request) is True


def test_is_admin_returns_false_when_header_missing():
    request = MagicMock()
    request.headers = {}

    assert _is_admin(request) is False


def test_require_admin_blocks_non_admin():
    request = MagicMock()
    request.headers = {}

    response = _require_admin(request)

    assert response.status_code == 403


def test_component_to_dict_returns_expected_structure():
    component = MagicMock()

    component.id = "1"
    component.brand = "NVIDIA"
    component.model = "RTX 4090"
    component.type = "GPU"
    component.base_specs = ""
    component.launch_year = 2022
    component.base_score = 36820.0
    component.created_at.isoformat.return_value = "2024-01-01T00:00:00"
    component.updated_at.isoformat.return_value = "2024-01-01T00:00:00"

    result = _component_to_dict(component)

    assert result["brand"] == "NVIDIA"
    assert result["model"] == "RTX 4090"
    assert "created_at" in result