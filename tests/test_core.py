import json
import tempfile
import unittest
from pathlib import Path

from local_dashboard_widget_sdk.core import ContractError, catalog, scaffold_widget, validate_preset, validate_widget
from local_dashboard_widget_sdk.schema import contract_schema
from local_dashboard_widget_sdk.typescript import typescript_definitions


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
            (root / "demo-widget.json").write_text(json.dumps(widget))
            data = catalog([root])
            self.assertEqual(data["total"], 1)
            self.assertEqual(data["byKind"], {"widget": 1})

    def test_contract_schema_shape(self):
        schema = contract_schema()
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIn("widget", schema["$defs"])
        self.assertIn("preset", schema["$defs"])
        self.assertIn("renderer", schema["$defs"])
        self.assertIn("oneOf", schema)

    def test_typescript_definitions_shape(self):
        text = typescript_definitions()
        self.assertIn("export interface DashboardWidgetManifest", text)
        self.assertIn("export type RendererKind", text)
        self.assertIn("export type DashboardContract", text)

    def test_preset_example_valid(self):
        preset = {
            "id": "stat-compact",
            "kind": "preset",
            "title": "Compact Stat",
            "renderer": "stat",
            "layout": {"minW": 1, "minH": 1, "defaultW": 2, "defaultH": 1},
            "defaults": {"unit": ""},
        }
        result = validate_preset(preset)
        self.assertEqual(result.id, "stat-compact")


if __name__ == "__main__":
    unittest.main()
