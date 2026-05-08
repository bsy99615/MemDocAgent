# `content_based.py`

## `sumy.evaluation.content_based.cosine_similarity` · *function*

## Summary:
Computes the cosine similarity between two term-frequency document models and returns the cosine of the angle between their raw term-frequency vectors (a float in the range 0.0 to 1.0 inclusive).

## Description:
This function treats each document model as a vector over the union of all terms observed in either model, computes the dot product of their raw term-frequency vectors, and divides by the product of their Euclidean magnitudes.

Known callers:
    - No direct callers were provided in the snapshot. In practice, it is used in evaluation stages that compare a produced/processed document model (evaluated_model) against a reference/ground-truth model (reference_model) to measure content overlap.

Reason for extraction:
    - Encapsulates the mathematical cosine-similarity operation so evaluation code can call a single, tested utility rather than duplicating the dot-product/magnitude logic across the codebase.

Responsibility boundary:
    - Only computes similarity from two models exposing the required interface (.terms, .term_frequency(term), .magnitude).
    - Does not perform tokenization, normalization, weighting (TF-IDF), or model construction—these are caller responsibilities.

## Args:
    evaluated_model (object)
        - Expected type: an instance of a Tf-style document model (intended to be sumy.models.TfDocumentModel) or any object that implements the required interface.
        - Required interface:
            * .terms: iterable of term keys (e.g., strings)
            * .term_frequency(term) -> numeric (non-negative integer for TfDocumentModel)
            * .magnitude -> float (Euclidean norm of raw term-frequency vector)
        - Note: The implementation performs an isinstance check using the symbol TfModel. If TfModel is undefined in the module namespace at runtime, a NameError will be raised before the ValueError described below. The intended check appears to be against TfDocumentModel.

    reference_model (object)
        - Same requirements as evaluated_model; represents the reference/ground-truth model.

Interdependencies:
    - Both models should use identical term normalization/casing so term keys align (TfDocumentModel lowercases terms at construction).
    - term_frequency is expected to return 0 when a term is absent (this is how TfDocumentModel behaves).

## Returns:
    float
        - The cosine similarity score computed as:
            numerator = sum_{t in union_of_terms} evaluated_model.term_frequency(t) * reference_model.term_frequency(t)
            denominator = evaluated_model.magnitude * reference_model.magnitude
            result = numerator / denominator
        - Range and interpretation:
            * 1.0 indicates vectors are proportional (maximum similarity).
            * 0.0 indicates no overlap of terms (dot product zero).
            * Any value between 0.0 and 1.0 inclusive for non-negative term-frequency vectors.
        - Edge values:
            * Exact 0.0 is returned when numerator == 0.0 (no shared terms or all frequencies are zero).
            * The function never returns NaN; instead it raises ValueError when the denominator is zero.

## Raises:
    ValueError:
        - If either argument fails the initial isinstance check, the function raises:
            "Arguments has to be instances of 'sumy.models.TfDocumentModel'"
          (Note: the code uses TfModel in the isinstance check; the message references TfDocumentModel.)
        - If the denominator equals 0.0 (one or both models have magnitude 0), the function raises:
            "Document model can't be empty. Given %r & %r" % (evaluated_model, reference_model)

    NameError (implementation caveat):
        - If the symbol TfModel is not defined in the module at runtime, the isinstance(...) expression will raise NameError before the ValueError can be raised. This is an apparent mismatch between the intended class name (TfDocumentModel) and the checked name (TfModel).

## Constraints:
Preconditions:
    - Both arguments must be objects that conform to the described interface (.terms iterable, .term_frequency(term), .magnitude float >= 0).
    - Preferably, both models were constructed with the same token normalization (e.g., both lowercased) so that the union of terms matches correctly.
    - For reliable execution, ensure TfModel (or the correct class symbol) is defined in the module namespace or adjust the code to check TfDocumentModel.

Postconditions:
    - No mutation of evaluated_model or reference_model.
    - Either returns a float in [0.0, 1.0] or raises ValueError/NameError as described.
    - Temporary set of unioned terms is not persisted; no external state is modified.

## Side Effects:
    - None. Function is pure with respect to I/O and global state (reads model attributes/methods only).

## Control Flow:
flowchart TD
    Start --> TypeCheck
    TypeCheck -->|isinstance checks both True| BuildUnion
    TypeCheck -->|any isinstance fails| RaiseTypeValueError
    BuildUnion --> ComputeNumeratorLoop
    ComputeNumeratorLoop --> ComputeDenominator
    ComputeDenominator -->|denominator == 0.0| RaiseEmptyValueError
    ComputeDenominator -->|denominator != 0.0| ReturnQuotient
    ReturnQuotient --> End
    RaiseTypeValueError --> End
    RaiseEmptyValueError --> End

Notes:
    - The union of terms is constructed as frozenset(evaluated_model.terms) | frozenset(reference_model.terms).
    - Numerator is computed by iterating once over that union and summing term-frequency products.
    - term_frequency calls are expected to be O(1) (as in TfDocumentModel where a Counter lookup is used).

## Complexity:
    - Time: O(U) where U is the number of unique terms in the union of both models (one pass over union).
    - Space: O(U) for the temporary frozenset used to represent the union of terms.

## Implementation details from TfDocumentModel (relevant behavior):
    - term frequencies are non-negative integers stored in a Counter; term keys are lowercased on construction.
    - magnitude is computed as sqrt(sum(count**2 for count in counts)), so magnitude == 0.0 for an empty model.

## Examples:

Example A — numeric walkthrough
    Given:
        evaluated_model term frequencies: { "a": 2, "b": 1 }
        reference_model term frequencies: { "a": 1, "c": 3 }

    Steps:
        union_of_terms = {"a","b","c"}
        numerator = (2*1) + (1*0) + (0*3) = 2
        magnitude_evaluated = sqrt(2**2 + 1**2) = sqrt(5) ≈ 2.23607
        magnitude_reference = sqrt(1**2 + 3**2) = sqrt(10) ≈ 3.16228
        denominator = 2.23607 * 3.16228 ≈ 7.07107
        result = numerator / denominator = 2 / 7.07107 ≈ 0.28284

    Interpretation:
        - Result ≈ 0.28284 indicates low-to-moderate overlap weighted by raw frequencies.

Example B — handling empty models
    - If either model has no terms (magnitude == 0.0), the function raises ValueError("Document model can't be empty. Given %r & %r" % (...)).
    - Wrap calls in try/except to handle or convert empty models before similarity computation.

Example C — defensive note about type check
    - If you hit NameError referencing TfModel, update the runtime environment so that TfModel is defined or modify the function to check isinstance(..., TfDocumentModel). The function's contract is duck-typed: any object implementing the required interface will work if the isinstance check is corrected or removed.

## `sumy.evaluation.content_based.unit_overlap` · *function*

## Summary:
Computes the Jaccard similarity between the vocabularies of two term-frequency document models, returning a float in [0.0, 1.0] that measures term-level overlap between the evaluated and reference documents.

## Description:
This function accepts two document-model objects that expose a .terms iterable (typically sumy.models.tf.TfDocumentModel). It builds sets from each model's terms, computes the number of shared terms (intersection), and returns intersection_size / union_size (the standard Jaccard index).

Known callers in this repository:
    - No direct callers were found in the scanned codebase memory.

Typical usage context:
    - Used during evaluation of automatically generated summaries or documents: after transforming a candidate and a reference text into TfDocumentModel objects, this function yields a simple content-based metric describing vocabulary overlap.

Why this is a standalone function:
    - Encapsulates a single, well-defined metric (term-level overlap). Separating this logic avoids duplication across different evaluation routines and centralizes validation and edge-case handling for this metric.

Important implementation note:
    - The implementation performs isinstance checks against the symbol TfModel, while the project defines TfDocumentModel. If TfModel is not defined in the module scope, calling this function will raise a NameError. To match intended behavior, the isinstance check should refer to TfDocumentModel (or the module should define TfModel as an alias).

## Args:
    evaluated_model (object)
        - Expected concrete type: sumy.models.tf.TfDocumentModel (or any object with a .terms iterable of term tokens, typically lowercase strings).
        - Role: model representing the evaluated (candidate) document or summary.
        - Notes: TfDocumentModel stores normalized (lowercased) tokens in an internal Counter and exposes .terms as the collection of unique terms. The function converts .terms into a frozenset for set operations.

    reference_model (object)
        - Expected concrete type: sumy.models.tf.TfDocumentModel (or any object with a .terms iterable of term tokens).
        - Role: model representing the reference (gold) document or summary.

Interdependencies:
    - Both arguments are required; the metric is undefined if both contain zero terms (this case triggers an error). If one model has terms and the other does not, the function returns 0.0.

## Returns:
    float
        - The Jaccard similarity of the two term sets:
            intersection_size / union_size
          where union_size = len(terms1) + len(terms2) - intersection_size.
        - Value range: 0.0 .. 1.0
            * 1.0: both models contain the same set of terms
            * 0.0: disjoint term sets (no shared terms)
        - Edge cases:
            * If one model has no terms and the other has terms, the result is 0.0.
            * If both models have no terms, the function raises ValueError to avoid a zero-division or meaningless similarity.

## Raises:
    NameError
        - Trigger: The source code references the symbol TfModel in the isinstance checks. If TfModel is not defined in the module namespace at call time, evaluating isinstance(...) will raise NameError.

    ValueError
        - Trigger A (type validation fails): If both arguments are not instances of the expected class (as checked by the implementation's isinstance against TfModel), the function raises:
            "Arguments has to be instances of 'sumy.models.TfDocumentModel'"
          (Note: this message references TfDocumentModel even though the code checks TfModel.)
        - Trigger B (both documents empty): If both term sets are empty (no terms in either model), the function raises:
            "Documents can't be empty. Please pass the valid documents."

## Constraints:
Preconditions:
    - Each argument must expose a .terms iterable (sequence or view of term strings). Prefer passing TfDocumentModel objects constructed with valid input (sequence of tokens or string + tokenizer).
    - The module scope must define (or alias) the symbol TfModel to refer to the intended document-model class, or the source should be corrected to check against TfDocumentModel.

Postconditions:
    - Inputs are not mutated.
    - On successful return, a float in [0.0, 1.0] is produced representing the term-overlap similarity.

## Side Effects:
    - None. The function performs pure in-memory computation without I/O, global mutation, or external service calls.

## Control Flow:
flowchart TD
    Start --> InstanceCheck
    InstanceCheck -->|TfModel undefined at runtime| NameError[Raise NameError]
    InstanceCheck -->|Both args are instances of TfModel| BuildSets
    InstanceCheck -->|Either arg not instance| TypeValueError[Raise ValueError: wrong type]
    BuildSets --> TermsSets[terms1 = frozenset(evaluated_model.terms); terms2 = frozenset(reference_model.terms)]
    TermsSets --> BothEmpty?
    BothEmpty? -->|Yes| EmptyValueError[Raise ValueError: documents empty]
    BothEmpty? -->|No| ComputeIntersection
    ComputeIntersection --> ComputeUnion[union = len(terms1) + len(terms2) - intersection]
    ComputeUnion --> Return[Return intersection / union]
    Return --> End

## Examples:
    - Basic usage (typical, happy path):
        1. Construct two TfDocumentModel instances from token sequences; note TfDocumentModel lowercases tokens and tracks term counts internally.
        2. Pass the two model objects to the function.
        3. Expect a float result where values closer to 1.0 indicate high vocabulary overlap.

    - Concrete usage pattern (pseudocode-like steps):
        model_a = TfDocumentModel(['this', 'is', 'a', 'test', 'test'])
        model_b = TfDocumentModel(['this', 'is', 'another', 'test'])
        similarity = unit_overlap(model_a, model_b)
        # similarity will be a float: intersection_terms = {'this','is','test'} => 3
        # union_terms = {'this','is','a','test','another'} => 5
        # similarity == 3 / 5 == 0.6

    - Handling the TfModel symbol issue:
        * If calling unit_overlap raises NameError because TfModel is undefined in the module scope, fix options include:
            - Define TfModel as an alias to TfDocumentModel in the module where unit_overlap is defined, e.g. set TfModel = TfDocumentModel before calling (module-level change).
            - Preferably, update the implementation to check isinstance(..., TfDocumentModel) to accurately reflect the intended type.

    - Error cases and handling:
        * If both models contain no terms, calling the function will raise ValueError; verify models were constructed correctly with non-empty inputs.
        * If the function raises ValueError about argument types, ensure the passed objects are instances of the expected document-model class (or expose a compatible .terms iterable).

Notes:
    - Because TfDocumentModel normalizes tokens to lowercase and exposes unique term keys via .terms, inputs with differing capitalization will be treated as the same token for this metric.

