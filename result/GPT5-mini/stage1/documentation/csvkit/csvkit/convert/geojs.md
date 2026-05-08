# `geojs.py`

## `csvkit.convert.geojs.geojson2csv` · *function*

## Summary:
Converts a GeoJSON FeatureCollection read from a file-like object into a CSV string where each row corresponds to a Feature and includes its id, flattened properties, the geometry as JSON, geometry type, and Point longitude/latitude when available.

## Description:
This function reads an open, readable file-like object containing a GeoJSON document and produces a CSV-formatted string representation of its features.

Known callers within the provided context:
    - No direct callers were present in the supplied file-level context. Typically this function is invoked by higher-level CLI or conversion utilities that accept GeoJSON input and need a CSV output string for downstream processing or writing to disk.

Why this logic is extracted into its own function:
    - It encapsulates the complete transformation from GeoJSON FeatureCollection to CSV string, handling JSON parsing, validation of top-level structure, extraction and ordering of property fields across features, normalization of geometries (including capturing Point coordinates), and CSV generation. Extracting into a function isolates parsing/validation and CSV formatting responsibilities so callers can simply pass a file-like object and receive a CSV string without duplicating parsing or validation logic.

## Args:
    f (file-like object): A readable file-like object (implements read()) positioned at the start of a JSON GeoJSON document. The function calls json.load(f), so f must contain valid JSON text representing a GeoJSON FeatureCollection.
    key (any, optional): Present in the signature for API compatibility. It is not used by the implementation and has no effect.
    **kwargs: Additional keyword arguments accepted but ignored by the implementation.

Notes on parameters:
    - 'f' must be readable and contain a top-level GeoJSON FeatureCollection object (a JSON object/dict with "type": "FeatureCollection" and a "features" array).
    - 'key' and '**kwargs' provide compatibility with generic conversion APIs; do not provide values expecting side effects.

## Returns:
    str: A CSV-formatted string (Unicode) representing the features. The CSV contains a header row followed by one row per feature.

    Header layout (columns in order):
        1. id - The feature 'id' value (feature.get('id')) or None if absent.
        2. One column per property discovered across all features. The order is the order in which unique property keys are first encountered while iterating the features list.
        3. geojson - The geometry object for the feature serialized as JSON text (json.dumps(geometry)).
        4. type - The geometry type string (geometry.get('type')) or None if geometry is None or lacks 'type'.
        5. longitude - For Point geometries with 'coordinates', the first coordinate element (index 0) or None if not available.
        6. latitude - For Point geometries with 'coordinates', the second coordinate element (index 1) or None if not available.

    Value normalization behavior:
        - If a property value is an OrderedDict instance, it is serialized to JSON text (json.dumps) before writing to CSV.
        - Geometry values are serialized with json.dumps even when None (json.dumps(None) produces "null") as written in the code path that constructs geometry strings.

## Raises:
    TypeError:
        - If the top-level JSON value is not a JSON object/dict: "JSON document is not valid GeoJSON: Root element is not an object."
        - If the top-level object lacks the "type" key: "JSON document is not valid GeoJSON: No top-level "type" key."
        - If the top-level "type" is not "FeatureCollection": "Only GeoJSON with root FeatureCollection type is supported. Not {actual_type}"
        - If the top-level object lacks the "features" key: "JSON document is not a valid FeatureCollection: No top-level "features" key."

    json.JSONDecodeError (subclass of ValueError):
        - If the input JSON is syntactically invalid, json.load(f) will raise json.JSONDecodeError.

    KeyError:
        - If an individual feature object does not contain the 'geometry' key, the implementation accesses feature['geometry'] directly and will raise KeyError. (Callers should ensure each feature contains a geometry key or pre-validate features.)

    Other exceptions:
        - If 'features' is not iterable (e.g., not a list), iteration may raise TypeError. Any exceptions thrown by agate.csv.writer or StringIO are propagated.

## Constraints:
Preconditions:
    - The file-like object 'f' must contain valid JSON and represent a GeoJSON FeatureCollection object (i.e., JSON object with "type": "FeatureCollection" and "features": an iterable of feature objects).
    - Each feature should be a mapping (dict-like) with optional keys 'id', 'properties', and 'geometry'. The function expects 'geometry' to be present (it will KeyError if missing).

Postconditions:
    - The function returns a CSV string whose header lists 'id', then all property fields discovered in encounter order, then 'geojson', 'type', 'longitude', and 'latitude'.
    - For every feature in the FeatureCollection, there will be a corresponding row in the CSV in the same order as the features array.
    - No global state is modified.

## Side Effects:
    - Reads data from the provided file-like object via json.load(f).
    - Uses an in-memory StringIO buffer to accumulate CSV data.
    - Calls agate.csv.writer to format CSV rows into the StringIO buffer.
    - No file system, database, network, or global state changes are performed by this function.

## Control Flow:
flowchart TD
    A[Start: call geojson2csv(f, key=None, **kwargs)] --> B[json.load(f) -> js]
    B --> C{is js a dict?}
    C -- No --> C1[Raise TypeError: Root element is not an object]
    C -- Yes --> D{'type' in js?}
    D -- No --> D1[Raise TypeError: No top-level "type" key]
    D -- Yes --> E{js['type'] == 'FeatureCollection'?}
    E -- No --> E1[Raise TypeError: Only FeatureCollection supported]
    E -- Yes --> F{'features' in js?}
    F -- No --> F1[Raise TypeError: No top-level "features" key]
    F -- Yes --> G[features = js['features']; initialize property_fields, features_parsed]
    G --> H[For each feature in features:]
    H --> I[properties = feature.get('properties', {}); extend property_fields in encounter order]
    I --> J[geometry = feature['geometry']  (may KeyError if missing)]
    J --> K{geometry is not null?}
    K -- Yes --> L[geometry_type = geometry.get('type')]
    K -- No --> L2[geometry_type = None]
    L --> M{geometry_type == 'Point' and 'coordinates' in geometry?}
    M -- Yes --> N[longitude, latitude = coordinates[0:2]]
    M -- No --> O[longitude, latitude = (None, None)]
    N --> P[features_parsed.append((id, properties, json.dumps(geometry), geometry_type, longitude, latitude))]
    O --> P
    P --> Q[After loop: build header = ['id'] + property_fields + ['geojson','type','longitude','latitude']]
    Q --> R[Create StringIO and agate.csv.writer; writer.writerow(header)]
    R --> S[For each entry in features_parsed: build row, json.dumps OrderedDict property values, writer.writerow(row)]
    S --> T[output = o.getvalue(); o.close(); return output]
    T --> Z[End]

## Examples:
Example happy-path usage:
    - Typical usage when reading a GeoJSON file into memory and converting to CSV:
        with open('input.geojson', 'r', encoding='utf-8') as fh:
            csv_text = geojson2csv(fh)
        # csv_text is a str containing the CSV representation; write to file or further process.

Example with error handling:
    try:
        with open('maybe_invalid.geojson', 'r', encoding='utf-8') as fh:
            csv_text = geojson2csv(fh)
    except json.JSONDecodeError as e:
        # Handle malformed JSON input
        raise
    except TypeError as e:
        # Handle non-FeatureCollection GeoJSON structures or missing keys
        raise
    except KeyError as e:
        # A feature was missing the 'geometry' key
        raise

Notes and recommendations for callers:
    - If features may omit 'geometry', normalize features before calling (e.g., ensure feature['geometry'] exists, possibly as None) to avoid KeyError.
    - If property values include nested ordered mappings, the function will JSON-serialize OrderedDict values; other nested mappings (plain dict) are left as-is and will be output by agate.csv.writer in their Python representation unless pre-serialized by the caller.
    - To preserve a deterministic column order for properties, ensure properties appear in a consistent order across features or precompute property field order before calling this function.

