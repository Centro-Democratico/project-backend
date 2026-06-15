from core.views import _videogame_to_dict, _recalculate_ranking
from unittest.mock import MagicMock, patch


def test_videogame_to_dict_maps_fields_correctly():
    game = MagicMock()

    game.id = "1"
    game.name = "Game"
    game.genre = "RPG"
    game.developer = "Dev"
    game.release_year = 2020

    result = _videogame_to_dict(game)

    assert result["name"] == "Game"
    assert result["genre"] == "RPG"
    assert result["release_year"] == 2020


@patch('core.views.HardwareComponent.objects.get')
@patch('core.views.BenchmarkSession.objects.filter')
def test_recalculate_ranking_computes_average(mock_filter, mock_get):

    cpu_component = MagicMock()
    gpu_component = MagicMock()


    def get_side_effect(*args, **kwargs):
        if kwargs.get("type") == "CPU":
            return cpu_component
        if kwargs.get("type") == "GPU":
            return gpu_component

    mock_get.side_effect = get_side_effect

    sessions = [MagicMock(score=100), MagicMock(score=200)]

    queryset = MagicMock()
    queryset.exists.return_value = True
    queryset.count.return_value = 2
    queryset.__iter__.return_value = sessions

    mock_filter.return_value = queryset

    session = MagicMock()
    session.hardware.cpu = "Intel"
    session.hardware.gpu = "Nvidia"

    _recalculate_ranking(session)

    assert cpu_component.base_score == 150
    assert gpu_component.base_score == 150

    cpu_component.save.assert_called_once()
    gpu_component.save.assert_called_once()




@patch('core.views.HardwareComponent.objects.get')
@patch('core.views.BenchmarkSession.objects.filter')
def test_recalculate_ranking_does_not_update_without_sessions(mock_filter, mock_get):

    component = MagicMock()
    mock_get.return_value = component

    queryset = MagicMock()
    queryset.exists.return_value = False

    mock_filter.return_value = queryset

    session = MagicMock()
    session.hardware.cpu = "Intel"
    session.hardware.gpu = "Nvidia"

    _recalculate_ranking(session)

    component.save.assert_not_called()