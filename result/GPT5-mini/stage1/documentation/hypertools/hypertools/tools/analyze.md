# `analyze.py`

## `hypertools.tools.analyze.analyze` · *function*

## Summary:
Orchestrate a three-stage preprocessing pipeline—normalization, dimensionality reduction, then alignment—and return the aligned result; this thin wrapper forwards parameters to each stage and returns whatever the alignment stage produces.

## Description:
- Known callers and context:
    - This function is intended as the primary convenience API for applying combinations of normalization, reduction, and alignment before visualization or downstream analysis.
    - The reduction utility warns users to prefer this function when combining transforms; therefore user-facing code or higher-level convenience wrappers typically call analyze when multiple transforms are needed.
    - Typical usage occurs in preprocessing pipelines immediately prior to plotting or further statistical analyses.

- Responsibility boundary:
    - analyze's sole responsibility is orchestration: call normalization → reduction → alignment in that order, forwarding relevant parameters and returning the final aligned result.
    - It does not implement normalization/reduction/alignment logic itself, nor does it mutate global state; it simply delegates to three callables (referred to in the implementation as normalizer, reducer, and aligner).

- Implementation note for reimplementers:
    - The function body references callables named normalizer, reducer, and aligner. In the codebase these are expected to refer to the normalization, reduction, and alignment implementations (commonly normalize, reduce, and align respectively). When reimplementing, ensure these names are bound appropriately (for example, by aliasing or wrapping the imported functions) so analyze can call them:
        * normalizer(x, normalize=..., internal=..., format_data=...)
        * reducer(x, reduce=..., ndims=..., internal=..., format_data=...)
        * aligner(x, align=...)
    - The exact accepted signatures of the underlying components determine behavior; analyze forwards parameters rather than transforming them.

## Args:
    data (list[2-D array] | 2-D array | other):
        - The dataset to process. Commonly a list of 2-D numeric arrays (e.g., per-subject time-by-features matrices) or a single 2-D numeric array that an input formatter will convert to the canonical list-of-2D-arrays form.
        - No strict type is enforced by analyze itself; validity is determined by the called normalizer/reducer/aligner.

    normalize (str | bool | None, optional):
        - Passed through to the normalization stage as normalize=normalize.
        - Typical allowed values (per the normalization implementation): 'across', 'within', 'row', False, or None.
        - Default: None. If False or None, normalization is skipped and the original data is forwarded.

    reduce (str | dict | object | None, optional):
        - Forwarded to the reduction stage as reduce=reduce.
        - Can be:
            * A model name string (e.g., 'IncrementalPCA') recognized by the reduction stage.
            * A dict of the form {'model': <model-or-name>, 'params': <params-dict>}.
            * A model-like object that implements fit_transform and exposes n_components.
        - Default: None. If None, reduction is skipped.

    ndims (int | None, optional):
        - Suggested dimensionality for reduction; forwarded to the reduction stage as ndims=ndims.
        - If both ndims and model_params contain n_components, reduction logic reconciles them (reducer may prefer ndims and emit a warning if they differ).

    align (Any, optional):
        - Forwarded to the alignment stage as align=align.
        - Interpretation depends on the alignment implementation (e.g., string algorithm name, configuration dict, or alignment object).
        - Default: None (no alignment).

    internal (bool, optional):
        - Forwarded to normalization and reduction as internal=internal.
        - Controls whether intermediate stages return lists (True or when multiple input items present) or return a single array (False when a single item is returned).
        - Default: False.

## Returns:
    Any
        - The direct return value from the alignment stage: aligner(reducer(normalizer(...), ...), align=align).
        - Possible concrete outcomes:
            * A list of 2-D numpy arrays when intermediate stages produce multiple outputs (e.g., multiple subjects) or when internal=True.
            * A single 2-D numpy array when intermediate stages collapse to a single result and internal=False.
        - analyze imposes no additional shape normalization; callers should consult the normalization/reduction/alignment implementations for precise shape guarantees.

## Raises:
    - analyze does not introduce explicit raises; exceptions from normalizer, reducer, or aligner propagate unchanged.
    - Examples of exceptions that may propagate (observed in the underlying implementations):
        * AssertionError: normalization enforces allowed values via an assert (message: "scale_type must be across, within, row or none.").
        * ValueError: reduction may raise ValueError for malformed dict parameters or unsupported model specifications.
        * KeyError / AttributeError: reduction may raise these while resolving named models or checking required model methods/attributes.
        * TypeError: if supplied model-like objects lack required callable attributes or mapping keys are of wrong types.
    - Warnings (not exceptions) that callers may observe:
        * Reduction emits warnings for deprecated argument usage, for unequal ndims vs n_components, or when data cannot be reduced due to insufficient rows. These are warnings from the reduction implementation and are not converted to exceptions.

## Constraints:
- Preconditions:
    - data must be acceptable to the normalization stage (the formatter used by normalize/reduce expects numeric 2-D arrays or a convertible structure).
    - If a reduction is requested, the reduce parameter must be a supported model name, a properly-formed dict, or a model-like object supporting fit_transform and n_components.
    - The alignment parameter must be valid for the chosen alignment implementation.

- Postconditions:
    - On successful return, the data have been passed through normalization, reduction, and alignment in order.
    - No global variables are modified by analyze itself; any mutations are due to the underlying components.

## Side Effects:
    - analyze itself performs no I/O and no logging beyond what the delegated functions do.
    - Side effects you must account for (from delegated components):
        * Normalization may call a formatter that allocates new arrays.
        * Reduction will instantiate model objects and call fit_transform (potentially expensive), and may emit warnings.
        * Alignment may allocate new arrays or mutate intermediate data structures depending on implementation.
    - Any warnings or exceptions coming from these operations propagate through analyze.

## Control Flow:
flowchart TD
    A[Start: analyze(data, normalize, reduce, ndims, align, internal)] --> B{normalize is None or False?}
    B -- Yes --> C[skip normalization -> normalized_data = data]
    B -- No --> D[Call normalizer(data, normalize=normalize, internal=internal)]
    D --> C
    C --> E{reduce is None?}
    E -- Yes --> F[skip reduction -> reduced_data = normalized_data]
    E -- No --> G[Call reducer(normalized_data, reduce=reduce, ndims=ndims, internal=internal)]
    G --> F
    F --> H{align is None?}
    H -- Yes --> I[skip alignment -> result = reduced_data]
    H -- No --> J[Call aligner(reduced_data, align=align)]
    J --> I
    I --> K[Return result]
    D -->|exception| X[propagate exception]
    G -->|exception| X
    J -->|exception| X

## Examples (realistic usage described in prose):
- Typical successful pipeline (prose example):
    1. You have per-subject time-by-features datasets represented as a list of 2-D numpy arrays.
    2. To z-score features across all subjects, reduce dimensionality to 3 with IncrementalPCA, and then apply a group alignment algorithm, call analyze with normalize='across', reduce='IncrementalPCA', ndims=3, and align set to your alignment configuration/object.
    3. analyze will (a) normalize the inputs according to the chosen normalize mode, (b) attempt to reduce dimensionality according to reduce and ndims (skipping reduction if not required), and (c) align the reduced outputs if align is provided. The returned value will be either a list of arrays or a single array depending on internal and input cardinality.

- Handling known edge cases (prose example):
    - If you pass normalize=False or normalize=None the normalization stage is skipped and the original data is forwarded unchanged.
    - If reduction is requested but the stacked data has only a single row, the reduction implementation returns a zero-filled array with length equal to ndims and may emit a warning. To handle this, validate input shapes before calling analyze or wrap the call in a try/except to catch unexpected ValueError or handle warnings.
    - If providing a custom model object to reduce, ensure it implements fit_transform and exposes n_components; otherwise reduction will raise ValueError or AttributeError.

