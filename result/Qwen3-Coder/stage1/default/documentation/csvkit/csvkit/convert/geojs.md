# `geojs.py`

## `csvkit.convert.geojs.geojson2csv` · *function*

## Summary:
Converts GeoJSON FeatureCollection data into CSV format with support for geometric coordinates.

## Description:
Transforms GeoJSON data containing features with properties and geometries into a tabular CSV representation. The function extracts all unique property fields and converts Point geometries into longitude and latitude columns while preserving other geometry data as JSON strings.

## Args:
    f (file-like object): Input file object containing valid GeoJSON FeatureCollection data
    key (any, optional): Unused parameter in current implementation (included for API compatibility)
    **kwargs: Additional keyword arguments (currently unused)

## Returns:
    str: CSV-formatted string containing the converted data with columns for id, properties, geojson, type, longitude, and latitude

## Raises:
    TypeError: When the JSON document is not valid GeoJSON or doesn't conform to expected structure
        - If root element is not a dictionary
        - If no top-level "type" key exists
        - If type is not "FeatureCollection"
        - If no top-level "features" key exists

## Constraints:
    Preconditions:
        - Input file must contain valid JSON data
        - JSON must represent a valid GeoJSON FeatureCollection
        - Features must be properly structured with optional properties and geometry objects
    Postconditions:
        - Output is a properly formatted CSV string with header row
        - All property fields from features are included as columns
        - Point geometries are parsed into longitude and latitude columns
        - Non-Point geometries are preserved as JSON strings

## Side Effects:
    - Reads from the input file object
    - Creates in-memory string buffer for CSV generation
    - No external I/O operations beyond file reading and string output

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
    G -- Yes --> H[Process features]
    H --> I[Extract property fields]
    I --> J[Parse geometry and coordinates]
    J --> K[Build CSV header]
    K --> L[Write header row]
    L --> M[Write data rows]
    M --> N[Return CSV string]
```

## Examples:
```python
# Basic usage with file object
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
        "coordinates": [12.34, 56.78, 90.12]
      }
    }
  ]
}
'''

with StringIO(geojson_data) as f:
    csv_output = geojson2csv(f)
    print(csv_output)
    # Output would be something like:
    # id,name,population,geojson,type,longitude,latitude
    # 1,Location A,1000,"{""type"": ""Point"", ""coordinates"": [12.34, 56.78, 90.12]}","Point",12.34,56.78
```

