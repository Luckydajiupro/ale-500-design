import unittest

from web.app import AppError, _set_path


class SuggestionPathTests(unittest.TestCase):
    def test_writes_into_list_item(self) -> None:
        payload = {"deliverables": [{"format": "json"}]}
        _set_path(payload, "deliverables[0].format", "xlsx")
        self.assertEqual(payload["deliverables"][0]["format"], "xlsx")

    def test_creates_nested_object(self) -> None:
        payload = {}
        _set_path(payload, "scenario.role", "审计师")
        self.assertEqual(payload, {"scenario": {"role": "审计师"}})

    def test_rejects_out_of_range_index(self) -> None:
        with self.assertRaises(AppError):
            _set_path({"deliverables": []}, "deliverables[1].format", "xlsx")


if __name__ == "__main__":
    unittest.main()
