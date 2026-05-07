# `geojs.py`

## `csvkit.convert.geojs.geojson2csv` · *function*

## Summary:
Converts a GeoJSON FeatureCollection into CSV format with structured geometry and property fields.

## Description:
This function transforms GeoJSON data containing a FeatureCollection into a CSV representation. It extracts properties from each feature and converts geometry data into structured columns including longitude and latitude for Point geometries. The function is designed to handle standard GeoJSON FeatureCollection formats and raises appropriate errors for invalid inputs.

## Args:
    f (file-like object): A readable file object containing valid JSON data representing a GeoJSON FeatureCollection.
    key (str, optional): Placeholder parameter with no current implementation; intended for future extension.
    **kwargs: Additional keyword arguments that are currently ignored.

## Returns:
    str: A CSV-formatted string containing the converted data with columns for id, properties, geojson, type, longitude, and latitude.

## Raises:
    TypeError: When the JSON document is not valid GeoJSON due to root element not being an object.
    TypeError: When the JSON document lacks a top-level "type" key.
    TypeError: When the GeoJSON type is not "FeatureCollection".
    TypeError: When the FeatureCollection lacks a top-level "features" key.

## Constraints:
    Preconditions:
        - Input file must contain valid JSON data
        - JSON data must represent a valid GeoJSON FeatureCollection
        - Root element must be a dictionary
        - Must contain a "type" key with value "FeatureCollection"
        - Must contain a "features" key with array value
    Postconditions:
        - Output is a properly formatted CSV string
        - CSV contains header row with expected column names: id, property fields, geojson, type, longitude, latitude
        - All properties from features are included as columns
        - Geometry data is serialized as JSON strings
        - Longitude and latitude are extracted only for Point geometries

## Side Effects:
    - Reads from the provided file object
    - Creates an in-memory StringIO buffer for CSV generation
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
    G -- Yes --> H[Parse features]
    H --> I[Extract properties and geometry]
    I --> J[Build header row]
    J --> K[Write header to CSV]
    K --> L[Process each feature]
    L --> M[Build CSV row]
    M --> N[Write row to CSV]
    N --> O[Return CSV output]
```

## Examples:
    # Basic usage with valid GeoJSON file
    with open('data.geojson', 'r') as f:
        csv_output = geojson2csv(f)
    
    # Processing a GeoJSON FeatureCollection with Point geometries
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": "1",
                "properties": {"name": "Location A", "population": 1000},
                "geometry": {
                    "type": "Point",
                    "coordinates": [-74.006, 40.7128, 10]
                }
            }
        ]
    }
    # Would produce CSV with columns: id, name, population, geojson, type, longitude, latitude

