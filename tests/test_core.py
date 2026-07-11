import tempfile
import unittest
from pathlib import Path

from local_dashboard_widget_sdk.core import ContractError, catalog, scaffold_widget, validate_widget


class CoreTests(unittest.TestCase):
    def test_scaffold_valid_widget(self):
        widget = scaffold_widget("demo-widget", "Demo Widget", "stat", "local-json")
        result = validate_widget(widget)
        self.assertEqual(result.id, "demo-widget")
        self.assertEqual(result.status, "draft")

    def test_refuses_bad_id(self):
        with self.assertRaises(ContractError):
            scaffold_widget("Bad_ID", "Bad", "stat", "local-json")

    def test_refuses_bad_table_contract(self):
        widget = scaffold_widget("demo-table", "Demo Table", "table", "local-json")
        widget["renderer"].pop("columns")
        with self.assertRaises(ContractError):
            validate_widget(widget)

    def test_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            widget = scaffold_widget("demo-widget", "Demo Widget", "stat", "local-json")
            (root / "demo-widget.json").write_text(__import__("json").dumps(widget))
            data = catalog([root])
            self.assertEqual(data["total"], 1)
            self.assertEqual(data["byKind"], {"widget": 1})


if __name__ == "__main__":
    unittest.main()
