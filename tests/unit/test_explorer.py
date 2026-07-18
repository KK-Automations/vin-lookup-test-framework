from unittest.mock import Mock, patch

from app.services.explorer import MIN_YEAR, ExplorerService


def make_service(settings, max_year=2027):
    return ExplorerService(settings, max_year=max_year)


class TestYearsAndMakes:
    def test_years_descend_from_next_year_to_1981(self, settings):
        years = make_service(settings, max_year=2027).years()
        assert years[0] == 2027
        assert years[-1] == MIN_YEAR

    def test_makes_curated_and_sorted(self, settings):
        makes = make_service(settings).makes()
        assert "Honda" in makes and "Tesla" in makes
        assert makes == sorted(makes, key=str.casefold)


class TestModels:
    @patch("app.services.explorer.requests.get")
    def test_models_fetched_and_cached(self, mock_get, settings):
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {"Results": [
                {"Model_Name": "Accord"}, {"Model_Name": "Civic"},
                {"Model_Name": "Accord"},
            ]},
            raise_for_status=lambda: None,
        )
        service = make_service(settings)

        first = service.models("Honda", 2003)
        second = service.models("Honda", 2003)

        assert first == ["Accord", "Civic"]
        assert second == first
        assert mock_get.call_count == 1

    @patch("app.services.explorer.requests.get")
    def test_fetch_failure_returns_empty(self, mock_get, settings):
        import requests

        mock_get.side_effect = requests.ConnectionError("boom")
        assert make_service(settings).models("Honda", 2003) == []
