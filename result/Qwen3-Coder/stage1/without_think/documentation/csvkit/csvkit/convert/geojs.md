# `geojs.py`

## `csvkit.convert.geojs.geojson2csv` · *function*

## Summary:
Converts GeoJSON FeatureCollection data into CSV format with geometry coordinates extracted.

## Description:
Transforms GeoJSON data containing a FeatureCollection into a CSV table format. Each GeoJSON feature becomes a row in the resulting CSV, with properties flattened into separate columns and geometric information extracted into longitude/latitude fields for Point geometries.

## Args:
    f (file-like object): Input stream containing valid GeoJSON FeatureCollection data
    key (str, optional): Unused parameter in current implementation
    **kwargs: Additional keyword arguments (currently unused)

## Returns:
    str: CSV-formatted string containing the converted data with columns: id, property fields, geojson, type, longitude, latitude

## Raises:
    TypeError: When input JSON is not valid GeoJSON or lacks required keys
        - If root element is not a dictionary
        - If no top-level "type" key exists
        - If type is not "FeatureCollection"
        - If no top-level "features" key exists

## Constraints:
    Preconditions:
        - Input file must contain valid JSON
        - JSON must represent a GeoJSON FeatureCollection
        - Each feature must have a geometry field
    Postconditions:
        - Output is a properly formatted CSV string
        - All property fields are included as columns
        - Point geometries have longitude/latitude extracted

## Side Effects:
    - Reads from the input file-like object
    - Creates in-memory string buffer for CSV generation
    - No external I/O operations beyond reading input

## Control Flow:
```mermaid
flowchart TD
    A[Start geojson2csv] --> B{Valid JSON?}
    B -- No --> C[Raise TypeError]
    B -- Yes --> D{Has "type" key?}
    D -- No --> C
    D -- Yes --> E{Type == "FeatureCollection"?}
    E -- No --> C
    E -- Yes --> F{Has "features" key?}
    F -- No --> C
    F -- Yes --> G[Process features]
    G --> H[Extract properties and geometry]
    H --> I[Build header row]
    I --> J[Write data rows]
    J --> K[Return CSV string]
```

## Examples:
```python
# Basic usage with file input
import io
geojson_data = '''{
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
}'''

with io.StringIO(geojson_data) as f:
    csv_output = geojson2csv(f)
    print(csv_output)
    # Output: "id,name,population,geojson,type,longitude,latitude\n1,Location A,1000,\"{\"type\":\"Point\",\"coordinates\":[-74.006,40.7128]}\",Point,-74.006,40.7128"
```

