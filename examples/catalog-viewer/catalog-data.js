window.LDW_CATALOG = {
  "schema": "local-dashboard-widget-sdk.catalog-viewer-data.v1",
  "generatedFrom": [
    "examples/widgets",
    "examples/presets"
  ],
  "summary": {
    "widgets": 2,
    "presets": 1,
    "renderers": [
      "stat",
      "table"
    ]
  },
  "widgets": [
    {
      "path": "examples/widgets/cpu-load.json",
      "contract": {
        "id": "cpu-load",
        "title": "CPU Load",
        "version": "0.1.0",
        "status": "production",
        "source": {
          "kind": "local-json",
          "path": "system.load",
          "refreshMs": 5000
        },
        "renderer": {
          "kind": "stat",
          "valuePath": "value",
          "unit": "%",
          "thresholds": [
            {
              "level": "warn",
              "gte": 75
            },
            {
              "level": "bad",
              "gte": 90
            }
          ]
        },
        "layout": {
          "minW": 1,
          "minH": 1,
          "defaultW": 2,
          "defaultH": 1
        },
        "tags": [
          "system",
          "production"
        ]
      }
    },
    {
      "path": "examples/widgets/service-table.json",
      "contract": {
        "id": "service-table",
        "title": "Service Table",
        "version": "0.1.0",
        "status": "lab",
        "source": {
          "kind": "local-json",
          "path": "services.items",
          "refreshMs": 10000
        },
        "renderer": {
          "kind": "table",
          "columns": [
            {
              "key": "name",
              "label": "Service"
            },
            {
              "key": "state",
              "label": "State"
            }
          ]
        },
        "layout": {
          "minW": 2,
          "minH": 1,
          "defaultW": 3,
          "defaultH": 2
        },
        "tags": [
          "system",
          "lab"
        ]
      }
    }
  ],
  "presets": [
    {
      "path": "examples/presets/stat-compact.json",
      "contract": {
        "kind": "preset",
        "id": "stat-compact",
        "title": "Compact stat panel",
        "renderer": "stat",
        "layout": {
          "minW": 1,
          "minH": 1,
          "defaultW": 2,
          "defaultH": 1
        },
        "defaults": {
          "unit": "",
          "thresholds": []
        }
      }
    }
  ]
};
