# `geojs.py`

## `csvkit.convert.geojs.geojson2csv` · *function*

## Summary:
Converts GeoJSON FeatureCollection data into CSV format with support for geometric coordinates.

## Description:
Transforms GeoJSON data containing features with properties and geometries into a CSV table format. The function processes each feature to extract ID, properties, geometry data, and geographic coordinates (longitude/latitude) for Point geometries. This extraction enables spatial data analysis in tabular formats while preserving all property fields and geometric information.

## Args:
    f (file-like object): Input stream containing valid GeoJSON FeatureCollection data
    key (str, optional): Parameter present in function signature but unused in implementation (default: None)
    **kwargs: Additional keyword arguments present in function signature but unused in implementation

## Returns:
    str: Complete CSV-formatted string containing header row followed by data rows with columns for id, all property fields, geojson, type, longitude, and latitude

## Raises:
    TypeError: When input JSON is not valid GeoJSON or lacks required structure elements
        - If root element is not a dictionary
        - If no top-level "type" key exists
        - If type is not "FeatureCollection"
        - If no top-level "features" key exists

## Constraints:
    Preconditions:
        - Input file must contain valid JSON
        - JSON must represent a GeoJSON FeatureCollection
        - Each feature must have a valid geometry object or None
        - Features must be iterable list of objects

    Postconditions:
        - Output CSV string contains properly formatted header row
        - All property fields from features are included as columns
        - Geometry data is serialized as JSON strings
        - Point geometries have longitude/latitude extracted and included

## Side Effects:
    - Reads from the input file-like object
    - Creates in-memory StringIO buffer for CSV construction
    - Uses agate.csv.writer for CSV formatting

## Control Flow:
```mermaid
flowchart TD
    A[Start geojson2csv] --> B{Valid JSON?}
    B -- No --> C[Raise TypeError]
    B -- Yes --> D{Root is dict?}
    D -- No --> C
    D -- Yes --> E{Has "type"?}
    E -- No --> C
    E -- Yes --> F{Type == "FeatureCollection"?}
    F -- No --> C
    F -- Yes --> G{Has "features"?}
    G -- No --> C
    G -- Yes --> H[Initialize features_parsed and property_fields]
    H --> I[Process each feature in features]
    I --> J{Feature has properties?}
    J -- Yes --> K[Add property keys to property_fields if not present]
    J -- No --> L[Skip property processing]
    L --> M[Extract geometry info]
    M --> N{Geometry exists?}
    N -- No --> O[Set geometry_type = None]
    N -- Yes --> P[Get geometry_type]
    P --> Q{Is Point geometry with coordinates?}
    Q -- Yes --> R[Extract longitude, latitude from coordinates[0:2]]
    Q -- No --> S[Set longitude, latitude = (None, None)]
    R --> T[Store feature tuple in features_parsed]
    S --> T
    T --> U[Build header with id, property_fields, geojson, type, longitude, latitude]
    U --> V[Create StringIO buffer and agate CSV writer]
    V --> W[Write header row]
    W --> X[Process each parsed feature]
    X --> Y[Build row with id, property values, geometry, type, longitude, latitude]
    Y --> Z[Write row to CSV]
    Z --> AA[Return CSV output string]
```

## Examples:
```python
# Basic usage with file input
import json
from io import StringIO

geojson_data = '''
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "id": "1",
      "properties": {"name": "Location A", "population": 1000},
      "geometry": {
        "type": "Point",
        "coordinates": [-74.006, 40.7128]
      }
    }
  ]
}
'''

with StringIO(geojson_data) as f:
    csv_output = geojson2csv(f)
    print(csv_output)
    # Output would be:
    # id,name,population,geojson,type,longitude,latitude
    # 1,Location A,1000,"{""type"": ""Point"", ""coordinates"": [-74.006, 40.7128]}","Point",-74.006,40.7128
```

