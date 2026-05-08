# `fft.py`

## `mingus.extra.fft._find_log_index` · *function*

## Summary:
Map a numeric frequency to its logarithmic bucket index using a global, monotonic lookup table and a small last-query cache; returns an integer index 0..127 for matched buckets or 128 to indicate "out of range" (too high or non-positive).

## Description:
This internal utility finds the index of the first bucket whose upper bound c satisfies cp < f <= c, where cp is the previous bucket's upper bound (0 for index 0). It uses two optimizations in this order:
1. A simple cache check against the most recently answered index (_last_asked) to quickly resolve repeated or nearby queries.
2. A binary search on the global ascending array _log_cache when the cache does not provide the answer.

Typical callers:
- Internal routines that map spectral peak frequencies or Hertz values into discrete logarithmic bins (e.g., converting FFT peak frequencies to note bins). These callers pass a positive frequency value and rely on the function to return a bucket index or 128 for out-of-range values.
- No callers were enumerated from the supplied context; treat this as an internal helper in the fft/audio analysis module.

Why split out:
- Encapsulates the mapping policy (cp < f <= c), caching behavior, and binary-search fallback in one place so other code can request bucket indices without duplicating search logic or caching concerns.

## Args:
    f (float | int)
        Frequency value to map into a logarithmic bucket.
        - Expected domain: numeric (int or float).
        - Semantics:
            * f <= 0: treated as out-of-range and returns 128.
            * 0 < f <= _log_cache[127]: candidate for an index 0..127.
            * f > _log_cache[127]: treated as out-of-range and returns 128 (unless _log_cache is longer and caller relies on additional entries; see Constraints).

Interdependencies:
- Behavior depends on module-global variables:
    * _log_cache: an indexable, ordered sequence of numeric bucket upper bounds.
    * _last_asked: either None or a tuple (last_index:int, last_value: numeric).
- The correctness of results and safety of indexing depend on invariants of these globals.

## Returns:
    int
        - 0..127: the index n such that _log_cache[n-1] < f <= _log_cache[n], where _log_cache[-1] is treated as 0 for n == 0.
          After returning an index in 0..127, the function sets _last_asked = (n, f) as a side effect.
        - 128: sentinel indicating "out of range" when f <= 0 or (as coded) f > _log_cache[127]. When 128 is returned the function does not update _last_asked.

Edge / boundary behaviors:
    - If f equals a bucket upper bound _log_cache[k] exactly, the function returns k (because cp < f <= c holds with c == f).
    - If f equals the lower bound of some bucket (which is the previous bucket's upper bound), the function returns the previous bucket index (k-1), not k.
    - The function will return 128 for non-positive f values.

## Raises:
    IndexError
        - If _log_cache is shorter than the implementation expects (see Constraints), indexing like _log_cache[127] or _log_cache[lastn + 1] may raise IndexError.
        - The cached-path access to _log_cache[lastn + 1] in particular can raise IndexError if lastn is the last valid index of _log_cache.
    TypeError
        - If f or elements of _log_cache are not mutually comparable (e.g., mixing incomparable types), Python may raise a TypeError during numeric comparisons.
    (These exceptions are not explicitly raised by the function via raise statements; they are Python runtime errors that occur when preconditions are violated.)

## Constraints:
Preconditions (caller responsibility):
    - _log_cache must be a sequence (list/tuple/numpy array) of numeric values in strictly increasing order.
    - The function's code explicitly references _log_cache[127] and may access _log_cache[lastn + 1] when _last_asked is present. To avoid out-of-bounds errors, ensure one of:
        * Preferred: len(_log_cache) >= 129 (indices 0..128 available). This guarantees the cached-path access _log_cache[lastn + 1] is safe even when lastn == 127.
        * Alternatively: if len(_log_cache) == 128 (indices 0..127), then ensure _last_asked is either None or its stored index < 127 so lastn + 1 will not be accessed out-of-range.
    - _last_asked, when not None, must be a tuple of the form (int_index, numeric_value) and int_index must be a valid index into _log_cache.
    - _log_cache must represent contiguous bucket upper bounds consistent with the invariant that for all i>0: _log_cache[i-1] < _log_cache[i].

Postconditions:
    - If return value is in 0..127: _last_asked is set to (returned_index, f).
    - If return value is 128: _last_asked is left unchanged by this function.

## Side Effects:
    - Mutates the module-global _last_asked to (index, f) on every successful mapping (returned index in 0..127).
    - No I/O, no networking, no filesystem or stdout writes, and no other globals are modified.

## Control Flow:
flowchart TD
    Start([Start])
    CheckLast{_last_asked is not None?}
    Start --> CheckLast
    CheckLast -- No --> RangeCheck
    CheckLast -- Yes --> UnpackLast[/(lastn,lastval) = _last_asked/]
    UnpackLast --> CompareLast{f >= lastval?}
    CompareLast -- No --> RangeCheck
    CompareLast -- Yes --> CheckLELast{f <= _log_cache[lastn]?}
    CheckLELast -- Yes --> UpdateLastReturn[(set _last_asked=(lastn,f))\nreturn lastn]
    CheckLELast -- No --> CheckLENext{f <= _log_cache[lastn+1]?}
    CheckLENext -- Yes --> UpdateLastNextReturn[(set _last_asked=(lastn+1,f))\nreturn lastn+1]
    CheckLENext -- No --> SetBegin[(begin = lastn)] --> RangeCheck
    RangeCheck{f > _log_cache[127] or f <= 0?}
    RangeCheck -- True --> Return128[(return 128)]
    RangeCheck -- False --> BinarySearchLoop[while begin != end:\n compute n=(begin+end)//2\n c=_log_cache[n]\n cp=_log_cache[n-1] if n!=0 else 0\n if cp < f <= c: set _last_asked=(n,f) and return n\n if f < c: end = n else begin = n]
    BinarySearchLoop --> ReturnIndex[(set _last_asked=(index,f))\nreturn index]

## Examples:
1) Minimal synthetic example (illustrative):
    # Precondition: monotonic increasing _log_cache with indices 0..128 available
    _log_cache = [0.0, 10.0, 20.0, 40.0, 80.0, 160.0] + [i*100.0 for i in range(6,129)]
    _last_asked = None

    idx = _find_log_index(30.0)
    # cp<30<=c matches where c == 40.0 (index 3), so idx == 3 and _last_asked == (3, 30.0)

    idx = _find_log_index(40.0)
    # exact upper bound: returns index 3 again (since cp < 40.0 <= c with c==40.0)

    idx = _find_log_index(0.0)
    # non-positive: returns 128 (out-of-range), _last_asked unchanged

2) Edge-case to avoid IndexError:
    If you create _log_cache with only 128 entries (indices 0..127), either:
    - Ensure _last_asked is None before any calls, or
    - Ensure any stored lastn in _last_asked is < 127
    Otherwise the cached-path test may attempt to access _log_cache[lastn + 1] and raise IndexError.

Notes:
    - This function is intended as an internal helper; callers should not rely on the numeric value 128 as a general-purpose sentinel beyond the module's convention documented here.
    - The cp < f <= c inequality is deliberate: frequencies that equal an upper bound belong to that bucket; frequencies equal to a lower bound belong to the previous bucket.

## `mingus.extra.fft.find_frequencies` · *function*

## Summary:
Produces a one-sided frequency vs. power spectrum from a block of time-domain samples, returning an ordered list of (frequency_in_Hz, power) pairs suitable for audio analysis.

## Description:
Transforms time-domain samples into a one-sided, normalized power spectrum by delegating the Fourier transform to a module-level helper named _fft, converting complex FFT bins into power values, applying DC and Nyquist corrections, and building the corresponding frequency axis.

Known callers within the codebase:
    - None discovered in the provided repository graph. Typical external callers are audio-analysis routines or feature extractors that pass a contiguous buffer of mono samples and expect per-bin frequency power information.

Why extracted:
    - Encapsulates the normalization and one-sided conversion logic so FFT computation, windowing, framing, and I/O remain separate. This allows consistent spectrum scaling across the codebase and simplifies unit testing.

## Args:
    data (sequence[float|int|complex]):
        - 1-D sequence of time-domain samples (list, tuple, or numpy array).
        - Must support len(data), indexing, and slicing.
        - Required: len(data) >= 1 (the function divides by n = len(data)).
    freq (int|float, optional):
        - Sampling rate (Hz) used to compute frequency bin spacing. Default: 44100.
        - Should be positive for meaningful frequency results; the function does not validate this and may raise errors (see Raises).
    bits (int, optional):
        - Bits per sample for compatibility with higher-level APIs (e.g., 8, 16, 24). Default: 16.
        - NOTE: This parameter is accepted but ignored by this function.

Interdependencies:
    - The function requires a callable _fft available in module scope. The expected contract:
        * _fft(data) returns an array-like of length n (len(data)), containing complex-valued FFT bins compatible with numpy.fft.fft semantics.
        * If _fft returns a different length, the function will slice or index that result; mismatches can cause IndexError or incorrect pairings.

## Returns:
    list[tuple[float, float]]:
        - A list of (frequency_hz, power) pairs representing the one-sided spectrum.
        - Length is uniquePts = ceil((n + 1) / 2.0) where n = len(data).
        - Frequencies start at 0 and increment by s = freq / float(n): [0, s, 2s, ..., (uniquePts-1)*s].
        - Power for each bin is computed from FFT bin X as:
            power = (abs(X) / n) ** 2 * 2
          applied to the first uniquePts bins (X[0:uniquePts]), then:
            - DC bin (index 0) is halved: p[0] = p[0] / 2.
            - If n is even, the Nyquist bin (last returned bin) is halved: p[-1] = p[-1] / 2.
        - All returned power values are non-negative.

Edge-case return behavior:
    - If _fft returns fewer items than expected, attempts to index p[0] will raise IndexError; otherwise slicing to p[0:uniquePts] will produce fewer power values and the final zip will pair only existing frequencies with powers.
    - If freq <= 0, the frequency axis is not meaningful; in particular, freq == 0 causes numpy.arange to be called with step s == 0 which raises a ValueError (see Raises).

## Raises:
    NameError:
        - Raised if _fft is not defined in module scope when the function attempts to call it.
    ZeroDivisionError:
        - If len(data) == 0, the function divides by n (normalization) and will raise ZeroDivisionError.
    IndexError:
        - If _fft returns an empty sequence or shorter sequence such that p[0] or p[-1] indexing occurs on an empty list, IndexError will be raised.
    ValueError:
        - If freq == 0 (or equivalently s == 0), numpy.arange(0, uniquePts * s, s) will raise a ValueError because the step argument is zero.
    TypeError:
        - If `data` is not a sequence (missing len(), indexing, or slicing) a TypeError may be raised by those operations.

## Constraints:
Preconditions:
    - data: non-empty 1-D sequence of numeric samples.
    - A callable _fft must exist in module scope and return an array-like with FFT results; ideally this is numpy.fft.fft or an equivalent.
    - freq should be positive to generate a valid frequency axis.

Postconditions:
    - Returns a list of uniquePts (ceil((n + 1) / 2.0)) (frequency, power) tuples with monotonically increasing frequency values and non-negative power values scaled per the implementation.

## Side Effects:
    - None. Function performs CPU-only computation and does not perform I/O or mutate module/global state. It depends on module-level _fft and numpy for operations.

## Control Flow:
flowchart TD
    Start --> Compute_n
    Compute_n --> Check_n_zero{n == 0?}
    Check_n_zero -- Yes --> Raise_ZeroDivisionError
    Check_n_zero -- No --> Invoke__fft
    Invoke__fft --> Receive_fft_output
    Receive_fft_output --> Compute_uniquePts
    Compute_uniquePts --> Slice_first_uniquePts
    Slice_first_uniquePts --> Compute_power_list[(abs(X)/n)**2*2]
    Compute_power_list --> Halve_DC[p[0] = p[0]/2]
    Compute_power_list --> Check_even_n{n % 2 == 0?}
    Check_even_n -- Yes --> Halve_Nyquist[p[-1] = p[-1]/2]
    Check_even_n -- No --> Skip_Nyquist_Adjust
    Halve_DC --> Compute_s[s = freq / n]
    Halve_Nyquist --> Compute_s
    Compute_s --> Build_freqArray[numpy.arange(0, uniquePts * s, s)]
    Build_freqArray --> Zip_freq_and_power
    Zip_freq_and_power --> Return_result
    Return_result --> End

## Examples:
Concrete numeric example (walkthrough):
    - Given data = [1.0, 0.0, -1.0, 0.0] and freq = 44100
      1) n = len(data) = 4
      2) Suppose _fft(data) behaves like numpy.fft.fft and returns X = [0.0, 2.0, 0.0, 2.0]
      3) uniquePts = ceil((4 + 1) / 2.0) = 3
      4) Take first uniquePts bins: [0.0, 2.0, 0.0]
      5) Scale to power: for each X, power = (abs(X)/n)**2 * 2
           - For X=0.0 -> (0/4)**2 * 2 = 0.0
           - For X=2.0 -> (2/4)**2 * 2 = (0.5)**2 * 2 = 0.5
           - For X=0.0 -> 0.0
      6) Halve DC: p[0] = 0.0 / 2 = 0.0
      7) n is even -> halve Nyquist bin: p[-1] = 0.0 / 2 = 0.0
      8) s = freq / float(n) = 44100 / 4 = 11025.0
      9) freqArray = numpy.arange(0, uniquePts * s, s) => [0.0, 11025.0, 22050.0]
     10) Returned spectrum: [(0.0, 0.0), (11025.0, 0.5), (22050.0, 0.0)]

Defensive caller pattern:
    - Validate inputs before calling to produce clearer errors:
        if len(data) == 0:
            raise ValueError("data must contain at least one sample")
        if freq <= 0:
            raise ValueError("freq must be positive")
        spectrum = find_frequencies(data, freq=freq)

## `mingus.extra.fft.find_notes` · *function*

## Summary:
Aggregate spectral peak amplitudes into discrete note bins and return a 129-entry list of (Note or None, summed_amplitude) tuples where indices 0–127 map to pitch Notes and index 128 is a catch-all for out-of-range peaks.

## Description:
This function consumes a sequence of (frequency, amplitude) pairs (a spectral-peak table) and accumulates amplitudes into logarithmic note buckets determined by the module helper _find_log_index. Each bucket index 0..127 corresponds to an absolute integer pitch which is converted into a Note instance using Note.from_int; bucket 128 is reserved for peaks that are out of the note-range or above the requested maxNote cutoff.

Known callers within the codebase:
- No explicit direct callers were found in the provided context. Typical callers are FFT/peak-analysis routines or WAV/file analysis helpers that produce freqTable (a list of (frequency, amplitude) peaks). In such pipelines find_notes is invoked after frequency peaks are extracted from an FFT, to map peaks to musical note bins and sum their strengths.

Why this logic is a separate function:
- Encapsulates the mapping from continuous frequency peaks to discrete note bins and the amplitude-accumulation policy (including the out-of-range bucket and maxNote cutoff). Separating this logic keeps FFT peak extraction and note-aggregation concerns decoupled and reusable.

## Args:
    freqTable (iterable of tuple[float|int, float|int]):
        - An iterable (e.g., list or generator) that yields 2-element tuples: (frequency_hz, amplitude).
        - frequency_hz: numeric (int or float). Expected domain: any real number; non-positive or invalid numeric values will be ignored or may cause downstream errors from _find_log_index.
        - amplitude: numeric (int or float). Values <= 0 are ignored (not accumulated).
        - Each yielded item must be unpackable into exactly two values; otherwise Python will raise an unpacking ValueError.
        - No internal normalization of amplitudes is performed — amplitudes are summed as provided.
    maxNote (int, optional, default=100):
        - Upper exclusive threshold for bucket indices considered valid note buckets.
        - If the computed bucket index f (returned by _find_log_index) is strictly less than maxNote, the amplitude is added to res[f].
        - If f is greater than or equal to maxNote, the amplitude is accumulated into the out-of-range bucket res[128].
        - Intended typical values: 0 <= maxNote <= 128. Using values >128 changes how the special sentinel value 128 is treated (see Constraints).

Interdependencies:
- Behavior relies on the semantics of _find_log_index:
    * It returns integers in 0..127 for in-range buckets or 128 as an out-of-range sentinel.
    * If _find_log_index returns 128 and maxNote > 128, that 128 value is compared to maxNote and may be treated as a normal index (see Constraints). The caller should set maxNote to a meaningful value (commonly <128) to preserve the intended sentinel semantics.

## Returns:
    list[tuple[Note | None, int|float]]:
        - A list of length 129. Each element is a 2-tuple (note_or_none, summed_amplitude).
        - For indices 0..127:
            * note_or_none is a new Note instance created by Note().from_int(index). The Note represents the pitch class and octave for that integer pitch index.
            * summed_amplitude is the accumulated amplitude (sum of all amplitudes from freqTable whose mapped index was this index and were > 0).
            * If no peaks mapped to that index, summed_amplitude is 0.
        - For index 128:
            * note_or_none is None (the sentinel for out-of-range or aggregated "too-high" peaks).
            * summed_amplitude is the sum of amplitudes mapped to the out-of-range bucket.
        - The order of the returned list corresponds to enumerate(res): element k is for bucket index k.

All possible return shapes / edge return values:
- Always returns a list of exactly 129 tuples.
- The second element (summed_amplitude) preserves whatever numeric type the amplitudes had (int or float) and will be 0 for buckets with no contributions.

## Raises:
    - ValueError:
        - If an item in freqTable does not unpack into exactly two values, Python raises ValueError during iteration/unpacking.
    - Any exceptions raised by _find_log_index (propagated):
        - e.g., IndexError if module globals used by _find_log_index are improperly sized, or TypeError for invalid comparisons — these propagate directly because find_notes does not catch them.
    - TypeError or other exceptions from Note.from_int:
        - Unlikely for indices 0..127 since Note.from_int expects integers, but if Note.from_int raises, the exception will propagate.
    - TypeError:
        - If amplitude values cannot be added to the running bucket totals (e.g., non-numeric amplitude), Python will raise a TypeError when attempting res[f] += ampl.

## Constraints:
Preconditions (caller must ensure):
    - freqTable yields (frequency, amplitude) pairs where frequency and amplitude are numeric types compatible with comparisons and addition.
    - _find_log_index and Note.from_int are available and behave according to their documented semantics (see module-level docs for _find_log_index and Note.from_int).
    - maxNote should be chosen so that sentinel index 128 remains distinct (typical maxNote < 128). If maxNote > 128, the integer 128 returned by _find_log_index may be treated as a valid index and cause its amplitude to be accumulated into the 128th bucket normally (which is still physically the last bucket and represented as None in the output).
Postconditions:
    - The returned list has length 129 and each element is (Note or None, summed_amplitude).
    - The function does not mutate freqTable; it only reads it.

## Side Effects:
    - No I/O (no files/network/stdout).
    - No modification of global state in this function itself.
    - Creates Note instances via Note().from_int for bucket indices 0..127 (these are new objects returned in the list).
    - Any side effects from _find_log_index (it mutates its module-global _last_asked) will occur because find_notes calls it.

## Control Flow:
flowchart TD
    Start([Start])
    Init[Initialize res list of 129 zeros]
    Iterate[For each (freq, ampl) in freqTable]
    Start --> Init --> Iterate
    CheckFreq{freq > 0?}
    Iterate --> CheckFreq
    CheckFreq -- No --> SkipItem[skip this pair]
    CheckFreq -- Yes --> CheckAmpl{ampl > 0?}
    CheckAmpl -- No --> SkipItem
    CheckAmpl -- Yes --> FindIdx[compute f = _find_log_index(freq)]
    FindIdx --> CheckMax{f < maxNote?}
    CheckMax -- Yes --> AddToBin[res[f] += ampl]
    CheckMax -- No --> AddToOut[res[128] += ampl]
    AddToBin --> Iterate
    AddToOut --> Iterate
    SkipItem --> Iterate
    Iterate --> BuildResult[map indices 0..127 to Note().from_int(index), 128 -> None and pair with summed amplitudes]
    BuildResult --> Return([return list of 129 (Note|None, amplitude) tuples])

## Examples:
1) Typical usage after FFT peak detection (happy path):
    freqTable = [(440.0, 1.0), (880.0, 0.5), (0.0, 2.0), (3000.0, 0.3)]
    # Call
    result = find_notes(freqTable, maxNote=100)
    # Interpretation:
    # - The peak at 440 Hz maps to a bucket index corresponding to the A4 integer; its amplitude 1.0 is added to that index.
    # - 880 Hz (an octave above) maps to its index and contributes 0.5.
    # - 0.0 Hz is ignored (non-positive frequency).
    # - 3000.0 Hz may map above maxNote and thus contribute to the None/128 catch-all bucket.
    # - result[k] gives (Note instance or None, summed_amplitude) for each bucket k.

2) Error handling example (defensive):
    try:
        result = find_notes(maybe_bad_freq_table, maxNote=100)
    except ValueError:
        # handle malformed entries that cannot be unpacked
        raise
    except IndexError:
        # _find_log_index encountered an out-of-bounds _log_cache condition
        raise

Notes:
    - The function does not perform pitch-to-note tuning or amplitude normalization — it only maps and sums amplitudes into integer buckets. Any further thresholding, peak selection, or normalization must be done by the caller.
    - Use a sensible maxNote (commonly <128) to preserve the special None sentinel at returned index 128.

## `mingus.extra.fft.data_from_file` · *function*

*No documentation generated.*

## `mingus.extra.fft.find_Note` · *function*

## Summary:
Return the musical pitch (a Note object) corresponding to the strongest aggregated spectral peak found in a block of time-domain audio samples; returns None if the strongest energy falls into the out-of-range bucket.

## Description:
This function performs a two-stage pipeline: it first converts raw time-domain samples into a one-sided frequency vs. power spectrum by calling the helper that produces (frequency_hz, power) pairs, then maps and aggregates those spectral peaks into discrete note buckets and selects the bucket with the largest total amplitude. Concretely:
1. Delegates time-domain → frequency-spectrum conversion to find_frequencies(data, freq, bits).
2. Delegates frequency→note aggregation to find_notes(...), which returns a 129-entry list of (Note | None, summed_amplitude) tuples (indices 0–127 map to Note instances, index 128 is an out-of-range sentinel with a None key).
3. Sorts the returned list by the summed_amplitude (the second tuple element) and returns the Note/None from the tuple with the largest amplitude.

Known callers:
- None discovered in the provided repository snapshot. Typical external callers are audio-analysis or pitch-detection pipelines that need the dominant pitch for a frame/block of samples (e.g., getting a single pitch estimate per analysis frame for melody extraction).

Why this logic is extracted:
- Encapsulates the orchestration of spectrum extraction and note-bucketing plus the selection policy for the dominant note. Keeping this selection logic in one small function avoids repeating the common pattern (spectrum → note buckets → choose max) across the codebase and establishes a clear boundary: callers provide raw samples and sampling parameters and receive the top note.

## Args:
    data (sequence[float|int|complex]):
        - 1-D sequence of time-domain audio samples (list, tuple, or numpy array).
        - Must support len(), indexing and slicing. Must be non-empty (len(data) >= 1).
        - Semantics and validation are those required by find_frequencies; invalid shapes or empty sequences may raise exceptions (see Raises).
    freq (int | float):
        - Sampling rate in Hz used to compute the frequency axis (e.g., 44100).
        - Should be positive; non-positive values will produce invalid frequency axes or propagate errors from find_frequencies (e.g., ValueError from zero step).
    bits (int):
        - Bits per sample (e.g., 8, 16, 24). This value is forwarded to find_frequencies for API compatibility; the frequency extraction implementation accepts it but may ignore it (see find_frequencies docs).

Notes on interdependencies:
- This function does not inspect or validate 'bits' itself; it relies on find_frequencies to accept and process it.
- The correctness of results depends on find_frequencies producing an expected sequence of (frequency, amplitude) pairs and on find_notes producing the canonical 129-entry bucket list.

## Returns:
    mingus.containers.note.Note | None
    - The Note instance corresponding to the note-bucket with the largest summed amplitude, or None if the highest-amplitude bucket is the out-of-range sentinel (index 128).
    - Behavior details:
        * Under normal operation (given the documented behavior of find_notes), find_notes returns exactly 129 tuples; the function sorts those tuples by their amplitude and selects the tuple with the largest amplitude.
        * If multiple buckets tie for the same largest amplitude, the chosen bucket is the one appearing last in the sorted order. The sort is stable: original ordering of equal-amplitude items (the order returned by find_notes) determines tie-breaking.
        * If find_notes were to return an empty iterable (contrary to its normal contract), attempting [-1] will raise IndexError (see Raises).

## Raises:
This function propagates exceptions from its callees and may raise or propagate the following errors:
    - ZeroDivisionError:
        - If find_frequencies divides by len(data) and len(data) == 0 (data must be non-empty).
    - ValueError:
        - If freq is zero (or otherwise invalid) and the frequency-axis construction in find_frequencies fails (e.g., numpy.arange step==0).
    - NameError:
        - If find_frequencies (or required module helper _fft) is missing from module scope and a NameError is raised when attempting to call it.
    - IndexError:
        - If find_notes returns an empty list or shorter-than-expected sequence and the code attempts to index [-1] or access tuple elements; or if underlying helpers (e.g., _find_log_index called by find_notes) raise IndexError; these propagate.
    - ValueError, TypeError, or other exceptions:
        - Any other exceptions raised by find_frequencies or find_notes (for example, unpacking errors, invalid numeric types, or errors from Note.from_int) are propagated unchanged.

## Constraints:
Preconditions:
    - data must be a non-empty, 1-D, indexable sequence of numeric audio samples.
    - freq should be a positive number representing the sample rate.
    - Module-level helpers required by find_frequencies and find_notes (e.g., _fft, _find_log_index, Note.from_int) must be available and behave as documented by their respective helpers.

Postconditions:
    - The function returns either a Note instance (dominant pitch) or None (dominant energy out-of-range).
    - It does not modify the input 'data' or any global module state (aside from any side effects from its callees).

## Side Effects:
    - None intrinsic to find_Note. It delegates processing to find_frequencies and find_notes which themselves are pure numeric computations (no I/O).
    - The function will create and return a Note instance (via find_notes); creating Note objects is the only observable allocation side effect.
    - Any side effects from find_frequencies/find_notes (e.g., exceptions or indirect mutation inside those helpers) are possible and will propagate.

## Control Flow:
flowchart TD
    Start --> Call_find_frequencies[Call find_frequencies(data, freq, bits)]
    Call_find_frequencies --> If_find_frequencies_raises{find_frequencies raises?}
    If_find_frequencies_raises -- Yes --> Propagate_Error[Propagate exception to caller]
    If_find_frequencies_raises -- No --> freqTable[Receive list of (frequency, amplitude) pairs]
    freqTable --> Call_find_notes[Call find_notes(freqTable)]
    Call_find_notes --> If_find_notes_raises{find_notes raises?}
    If_find_notes_raises -- Yes --> Propagate_Error
    If_find_notes_raises -- No --> notes_list[Receive list of (Note|None, amplitude) tuples]
    notes_list --> If_empty{notes_list empty?}
    If_empty -- Yes --> IndexError_Raised[Attempting [-1] raises IndexError]
    If_empty -- No --> Sort_by_amplitude[sorted(notes_list, key=item[1])]
    Sort_by_amplitude --> Pick_last[Pick last tuple (largest amplitude)]
    Pick_last --> Extract_note[Return tuple[0] (Note or None)]
    Extract_note --> End

## Examples:
Happy-path example (described):
    - Given a frame of mono audio samples (e.g., a numpy array of length 4096) at 44100 Hz:
      * Call find_Note(samples, 44100, 16).
      * Internally: find_frequencies builds a one-sided spectrum; find_notes aggregates spectrum power into 129 note buckets; find_Note selects the bucket with the largest summed amplitude and returns its Note object.
      * If the dominant bucket corresponds to A4, the function returns the Note instance representing A4; if the dominant energy is above the handled note range, it returns None.

Defensive caller pattern (error handling):
    - Validate inputs before calling:
      * Ensure len(data) > 0.
      * Ensure freq > 0.
    - Wrap the call in try/except to handle propagated errors from lower-level helpers (e.g., ValueError, IndexError) and provide fallback behavior or user-friendly error messages.

Notes:
    - The function's correctness and robustness depend on the documented contracts of find_frequencies and find_notes. It is a small orchestration helper: no spectrum or bucket-processing logic is performed here beyond delegating and selecting the maximum-amplitude bucket.

## `mingus.extra.fft.analyze_chunks` · *function*

## Summary:
Process a time-series of audio samples in fixed-size frames and return, for each frame, the single strongest mapped musical Note (or None) determined by per-frame spectral analysis.

## Description:
analyze_chunks slices the input sample sequence into contiguous blocks of size chunksize, runs spectral analysis on each block (via find_frequencies), maps spectral peaks to discrete musical note buckets (via find_notes), and selects the bucket with the largest accumulated amplitude. The function returns a list whose i-th element is the Note (or None sentinel) corresponding to the strongest detected note for the i-th block.

Known callers within the codebase:
- No explicit callers were found in the provided repository graph. Typical external callers are higher-level audio analysers or file-processing pipelines that:
    - load or stream raw mono samples into a list,
    - call analyze_chunks(data, sampling_rate, bits, chunksize) to obtain per-frame predominant notes,
    - then post-process the returned note sequence for melody extraction, visualization, or transcription.

Why this logic is a separate function:
- It encapsulates the framing-loop and per-frame orchestration (call find_frequencies, then find_notes, then pick the top bin). This keeps chunking and peak-selection separate from the lower-level spectrum and note-aggregation logic, enabling reuse of find_frequencies/find_notes and easier testing of the framing/pipeline behavior.

## Args:
    data (list-like of numbers):
        - A 1-D iterable sequence of time-domain audio samples (e.g., a Python list of floats/ints).
        - Expected to support slicing: data[:chunksize] and data[chunksize:].
        - Important: implementation relies on comparing the container to [] for emptiness (while data != []), so the recommended type is a Python list. Using other sequence types that do not compare equal to [] when empty may cause incorrect termination.
        - Precondition: contains the samples to analyze; may be any length >= 0 (see Raises).
    freq (int | float):
        - Sampling rate in Hz used by find_frequencies to compute frequency bins (commonly 44100).
        - Should be positive; passing non-positive values may cause downstream errors in find_frequencies.
    bits (int):
        - Bits per sample (e.g., 8, 16, 24). This parameter is forwarded to find_frequencies and retained for API compatibility even if ignored by downstream helpers.
    chunksize (int, optional, default=512):
        - Number of samples per analysis frame.
        - Must be a positive integer. The function processes successive non-overlapping frames of this length; the last frame may be shorter if len(data) is not a multiple of chunksize.

Interdependencies between parameters:
- chunksize controls how many samples are passed to find_frequencies per iteration; smaller chunksize increases temporal resolution but reduces frequency resolution in the spectral analysis performed by find_frequencies.

## Returns:
    list[Note | None]:
        - A list with one element per processed chunk (i.e., ceil(len(data) / chunksize) for a Python list input).
        - Each element is either:
            * a Note instance (the Note with the largest accumulated amplitude for that chunk), or
            * None (the sentinel returned when the strongest amplitude bucket is the out-of-range bucket produced by find_notes).
        - If a frame contains no valid spectral energy or if note aggregation maps the strongest energy to the out-of-range bucket, None may be returned for that frame.

Edge-case return behavior:
- If data is empty (len == 0) and is a Python list, the function returns an empty list [] without calling the helpers.
- If find_notes returns a list where all amplitudes are equal (tie), the sorted(...)[-1] behavior selects the last item in the sorted order; that item may be the None sentinel if it ties for largest amplitude.
- If find_notes returns an unexpected empty sequence or raises an exception, that exception will propagate (see Raises).

## Raises:
    Any exception raised by the underlying helpers or by invalid inputs is propagated. Typical possibilities:
    - ZeroDivisionError or ValueError from find_frequencies if it is invoked with an empty chunk or invalid freq (e.g., freq == 0).
    - IndexError if find_notes returns an empty sequence (sorted(...)[-1] would fail).
    - TypeError if data does not support slicing or comparison to [] (e.g., passing a non-sequence).
    - Any other exceptions raised by find_frequencies or find_notes (e.g., from invalid numeric types) propagate unchanged.

## Constraints:
Preconditions:
    - data should be a Python list (or list-like) of numeric samples so that successive slicing and comparison to [] behaves as intended.
    - freq must be a positive numeric sampling rate suitable for find_frequencies.
    - chunksize must be a positive integer.

Postconditions:
    - The returned list length equals the number of non-empty chunks processed (for list input: ceil(original_len / chunksize)).
    - For each returned element, the value is exactly the Note or None object produced by selecting the bucket with maximal summed amplitude from find_notes for that frame.

## Side Effects:
    - No I/O operations (no file, network, or stdout activity) are performed.
    - The function calls find_frequencies and find_notes; any side effects from those functions (e.g., if they mutate module globals) will occur.
    - No mutation of the original data list occurs by analyze_chunks itself beyond slicing (the implementation rebinds the local variable data to successive slices).

## Control Flow:
flowchart TD
    Start --> CheckDataEmpty{data != []?}
    CheckDataEmpty -- No --> ReturnEmptyList[return []]
    CheckDataEmpty -- Yes --> LoopStart[Take chunk = data[:chunksize]]
    LoopStart --> CallFindFreqs[call find_frequencies(chunk, freq, bits)]
    CallFindFreqs --> FreqResult
    FreqResult --> CallFindNotes[call find_notes(FreqResult)]
    CallFindNotes --> NotesResult
    NotesResult --> SortAndPick[sorted(..., key=item[1]) -> pick last -> get [0]]
    SortAndPick --> AppendResult[append Note_or_None to res]
    AppendResult --> SliceData[data = data[chunksize:]]
    SliceData --> CheckDataEmpty
    CheckDataEmpty -->|Yes| LoopStart
    CheckDataEmpty -->|No| ReturnRes[return res]
    ReturnRes --> End

## Examples:
1) Typical usage (happy path):
    - Given a Python list samples of mono audio, sampling rate 44100, 16 bits, and chunksize 512:
      result = analyze_chunks(samples, 44100, 16, chunksize=512)
      # result is a list of Note or None values, one per processed frame.

2) Defensive usage with validation:
    - Validate inputs to get clearer errors before calling:
      if not isinstance(samples, list):
          samples = list(samples)
      if len(samples) == 0:
          # no frames to analyze
          notes = []
      else:
          try:
              notes = analyze_chunks(samples, freq=44100, bits=16, chunksize=512)
          except Exception as e:
              # handle or log error (e.g., bad sampling rate, helper failures)
              raise

3) Interpreting results:
    - Iterate over returned notes to reconstruct a time-aligned sequence of predominant pitches (frame index * chunksize / freq gives approximate time of each frame).

## `mingus.extra.fft.find_melody` · *function*

## Summary:
Produce a run-length encoded sequence of consecutive predominant notes extracted from an audio file; the result is a list of (Note_or_None, consecutive_frame_count) tuples.

## Description:
- Known callers:
    - No callers were discovered in the provided repository graph. Typical usage is from higher-level audio-processing or transcription utilities that need a compact representation of the melodic sequence extracted from an audio file.
    - This function is normally called when the caller has an audio file path and wants a simple melody summary: the predominant note per analysis frame aggregated into contiguous durations.

- Responsibility boundary:
    - This function orchestrates file loading and per-frame spectral note detection, then compresses the frame-wise note sequence into run-length encoding (merge adjacent identical notes and count how many consecutive frames each note persisted).
    - It delegates file reading to data_from_file(file) which must return (data, sampling_rate, bits) and spectral/note extraction to analyze_chunks(data, sampling_rate, bits, chunksize).
    - The function intentionally does not perform pitch smoothing, timing conversion, or any further musical analysis — it only converts framewise results into (note, count) runs.

## Args:
    file (str, optional)
        - Path to an audio file (default: "440_480_clean.wav").
        - Must be a path accepted by the repository's data_from_file helper (usually a readable WAV file path).
    chunksize (int, optional)
        - Number of samples per analysis frame passed to analyze_chunks (default: 512).
        - Must be a positive integer. Smaller values increase temporal resolution and reduce spectral resolution; larger values do the opposite.
        - Interdependency: chunksize is forwarded directly to analyze_chunks and therefore affects how many frames will be produced and how note boundaries are detected.

## Returns:
    list[tuple(Note | None, int)]
        - Each element is a 2-tuple:
            * First element: a Note instance (from mingus.containers.note.Note) representing the predominant pitch for the run, or None if no valid note was identified for those frames.
            * Second element: a positive integer count giving the number of consecutive analysis frames (of length chunksize samples each) for which the first element was equal.
        - If analyze_chunks yields an empty sequence (no frames), an empty list is returned.
        - Example return: [(Note("A-4"), 3), (None, 1), (Note("G-4"), 5)] — meaning A-4 persisted for 3 consecutive frames, then a frame with no note, then G-4 for 5 frames.

## Raises:
    - Any exception raised by data_from_file(file) — for example, FileNotFoundError, wave errors, or unpacking/format errors if the helper returns unexpected values.
    - Any exception raised by analyze_chunks(data, sampling_rate, bits, chunksize) — for example, ValueError, IndexError, or TypeError arising from invalid inputs or internal processing.
    - A ValueError/TypeError may occur if data_from_file does not return a 3-tuple (data, freq, bits) (unpacking error).
    - Exceptions are not caught; they propagate to the caller so callers can handle I/O and processing failures explicitly.

## Constraints:
- Preconditions:
    - The file parameter must point to a readable audio file for data_from_file, or data_from_file must otherwise accept the provided argument.
    - chunksize must be a positive integer.
    - analyze_chunks expects data to be a sequence of numeric samples (commonly a Python list); data_from_file must supply such a sequence.
- Postconditions:
    - The returned list represents consecutive runs of identical per-frame notes as produced by analyze_chunks; the sum of the run counts equals the number of frames produced by analyze_chunks (for list-like data input).
    - No modifications are made to the original audio file; no global state is intentionally mutated by this function itself.

## Side Effects:
- Indirect I/O: calls data_from_file(file) which typically reads the specified audio file from disk; thus calling find_melody performs file I/O via that helper.
- Calls analyze_chunks which performs CPU-bound spectral analysis; this may allocate memory and perform CPU work but does not perform I/O itself.
- No direct writes to stdout, files, databases, or external services are performed by this function.

## Control Flow:
flowchart TD
    Start --> CallDataFromFile[data_from_file(file) -> (data, sampling_rate, bits)]
    CallDataFromFile --> ForEachFrame[for d in analyze_chunks(data, sampling_rate, bits, chunksize)]
    ForEachFrame --> CheckResEmpty{res != []?}
    CheckResEmpty -- No --> AppendFirst[res.append((d, 1))]
    CheckResEmpty -- Yes --> CompareLast{res[-1][0] == d?}
    CompareLast -- True --> IncrementLast[res[-1] = (d, res[-1][1] + 1)]
    CompareLast -- False --> AppendNew[res.append((d, 1))]
    AppendFirst --> ContinueLoop
    IncrementLast --> ContinueLoop
    AppendNew --> ContinueLoop
    ContinueLoop --> ForEachFrame
    ForEachFrame --> AfterLoop[return [(x, freq) for (x, freq) in res]]
    AfterLoop --> End

Note: The final return comprehension returns the same tuples collected in res (first element is the detected Note or None, second is the run count). The use of the name 'freq' as the second unpacked name in the comprehension shadows the earlier sampling_rate variable but does not change the runtime result (it is simply the run count).

## Examples:
1) Basic usage:
    - Extract an aggregated melody summary from a WAV file:
      runs = find_melody("song_excerpt.wav", chunksize=512)
      # runs is a list of (Note|None, int) describing consecutive identical-frame runs.

2) Handling file errors:
    try:
        runs = find_melody("nonexistent.wav")
    except Exception as exc:
        # data_from_file raised (e.g., FileNotFoundError or wave.Error)
        handle_error(exc)

3) Converting run counts to approximate durations:
    - Given runs = find_melody("file.wav", chunksize=512) and sampling_rate s returned internally by data_from_file:
      # To get time per frame: frame_duration = chunksize / sampling_rate
      # To convert runs into (note, seconds):
      # Note: find_melody does not return sampling_rate; callers requiring absolute time should re-run data_from_file or call data_from_file prior to find_melody.
      # Example pattern:
      data, sampling_rate, bits = data_from_file("file.wav")
      runs = find_melody("file.wav", chunksize=512)
      frame_duration = 512.0 / sampling_rate
      durations = [(note, count * frame_duration) for (note, count) in runs]

