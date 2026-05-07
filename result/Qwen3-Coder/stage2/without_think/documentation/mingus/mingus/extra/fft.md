# `fft.py`

## `mingus.extra.fft._find_log_index` · *function*

## Summary:
Finds the appropriate index in a logarithmic frequency cache for a given frequency value using optimized lookup with caching.

## Description:
This private helper function performs efficient index lookup in a pre-computed logarithmic frequency cache. It uses a hybrid approach that includes direct cache hit checking, range validation, and binary search to quickly locate the appropriate index for a given frequency value. The function is designed to optimize performance when processing sequences of frequencies by caching previous lookup results.

## Args:
    f (float): The frequency value to find the corresponding index for. Must be positive.

## Returns:
    int: The index in the logarithmic cache that corresponds to the given frequency. Returns 128 if the frequency is out of valid range.

## Raises:
    None explicitly raised in the function implementation.

## Constraints:
    Preconditions:
    - Global variable _log_cache must be initialized with at least 128 elements
    - Global variable _last_asked must be either None or a tuple of (index, frequency)
    - Input frequency f must be a positive number
    
    Postconditions:
    - Returns an integer index between 0 and 128 inclusive
    - When index > 0, it satisfies _log_cache[index-1] < f <= _log_cache[index]

## Side Effects:
    - Modifies the global variable _last_asked to cache the most recent lookup result
    - Accesses the global variable _log_cache (read-only)

## Control Flow:
```mermaid
flowchart TD
    A[Start _find_log_index(f)] --> B{Is _last_asked None?}
    B -- Yes --> C[Check f > _log_cache[127] or f <= 0?]
    C -- Yes --> D[Return 128]
    C -- No --> E[Binary search loop]
    E --> F[Calculate n = (begin + end) // 2]
    F --> G[Get c = _log_cache[n], cp = _log_cache[n-1] if n>0 else 0]
    G --> H{cp < f <= c?}
    H -- Yes --> I[Set _last_asked = (n, f)]
    I --> J[Return n]
    H -- No --> K{f < c?}
    K -- Yes --> L[end = n]
    K -- No --> M[begin = n]
    L --> N[begin != end?]
    M --> N
    N -- Yes --> F
    N -- No --> O[Set _last_asked = (begin, f)]
    O --> P[Return begin]
    B -- No --> Q[(lastn, lastval) = _last_asked]
    Q --> R[f >= lastval?]
    R -- Yes --> S[f <= _log_cache[lastn]?]
    S -- Yes --> T[Return lastn]
    S -- No --> U[f <= _log_cache[lastn+1]?]
    U -- Yes --> V[Return lastn+1]
    U -- No --> W[begin = lastn]
    W --> X[Check f > _log_cache[127] or f <= 0?]
    X -- Yes --> D
    X -- No --> E
```

## Examples:
    # Typical usage in frequency processing pipeline
    freq = 440.0  # A4 note frequency
    index = _find_log_index(freq)  # Returns appropriate cache index
    
    # Sequential processing optimization
    freq1 = 220.0
    freq2 = 440.0
    idx1 = _find_log_index(freq1)  # Performs full lookup
    idx2 = _find_log_index(freq2)  # Uses cached optimization

## `mingus.extra.fft.find_frequencies` · *function*

## Summary:
Computes frequency spectrum from audio data by applying FFT and normalizing power values.

## Description:
Performs Fast Fourier Transform analysis on audio sample data to extract frequency components and their corresponding power levels. This function is designed to process audio signals and return a mapping of frequencies to power values, making it useful for audio analysis applications such as pitch detection, spectral analysis, and audio visualization.

The function extracts only the unique frequency points (due to symmetry in real FFT) and properly normalizes the power values to account for the FFT scaling and windowing effects. Note that the bits parameter is currently unused in the implementation.

The function delegates the actual FFT computation to an internal `_fft` helper function, which is responsible for performing the mathematical FFT operation on the input data.

## Args:
    data (array-like): Audio sample data points, typically representing amplitude values over time
    freq (int): Sampling frequency in Hz, defaults to 44100 (standard CD quality)
    bits (int): Audio bit depth parameter (currently unused in implementation), defaults to 16 bits

## Returns:
    list[tuple[float, float]]: List of (frequency, power) tuples representing the frequency spectrum. Each tuple contains:
        - frequency (float): Frequency value in Hz
        - power (float): Normalized power level at that frequency

## Raises:
    None explicitly documented in the source code

## Constraints:
    Preconditions:
        - data must be a sequence of numeric values representing audio samples
        - freq must be a positive integer representing sampling frequency
        - bits must be a positive integer representing bit depth (though currently unused)
    
    Postconditions:
        - Returns a list of tuples with increasing frequency values
        - Power values are normalized and represent relative energy at each frequency bin
        - The first frequency value is 0 Hz (DC component)
        - The last frequency value is approximately half the sampling frequency (Nyquist limit)

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start find_frequencies] --> B{data length}
    B --> C[Calculate n = len(data)]
    C --> D[Call _fft(data)]
    D --> E[Calculate uniquePts = ceil((n+1)/2)]
    E --> F[Normalize FFT results]
    F --> G[Adjust DC component]
    G --> H[Adjust Nyquist component if n even]
    H --> I[Calculate frequency spacing s = freq/n]
    I --> J[Create frequency array]
    J --> K[Zip frequency and power arrays]
    K --> L[Return list of (freq, power) tuples]
```

## Examples:
    # Basic usage with default parameters
    audio_samples = [0.1, 0.2, 0.3, 0.4, 0.3, 0.2, 0.1]
    frequencies = find_frequencies(audio_samples)
    # Returns list of (frequency, power) tuples
    
    # Usage with custom sampling rate
    frequencies = find_frequencies(audio_samples, freq=22050)
    # Processes audio at 22kHz sampling rate

## `mingus.extra.fft.find_notes` · *function*

## Summary
Processes frequency-amplitude pairs from a Fast Fourier Transform analysis and maps them to musical notes, aggregating amplitudes for each note.

## Description
Converts frequency-domain audio data into musical note representations by mapping frequency bins to musical notes. This function is part of the audio processing pipeline that analyzes audio signals using FFT and translates the resulting frequency spectrum into playable musical notes.

The function aggregates amplitude values for each musical note, handling frequencies outside the valid range by grouping them under a special "out of range" bucket. It's designed to work with the output of FFT analysis where each entry represents a frequency bin with associated amplitude.

## Args
- freqTable (list[tuple[float, float]]): List of (frequency, amplitude) pairs representing the frequency spectrum from FFT analysis. Frequencies should be positive real numbers, and amplitudes should be non-negative.
- maxNote (int, optional): Maximum note index to consider for mapping. Notes with indices greater than or equal to this value are grouped into the overflow bucket. Defaults to 100.

## Returns
- list[tuple[Note or None, Note]]: List of tuples where each tuple contains:
  - First element: Note object representing the mapped musical note (or None for overflow bucket)
  - Second element: Empty Note object (used for consistency in the return structure)

## Raises
- None explicitly raised by this function

## Constraints
- Preconditions:
  - freqTable must be iterable containing (frequency, amplitude) pairs
  - Frequency values must be numeric and positive
  - Amplitude values must be numeric and non-negative
  - maxNote must be a non-negative integer

- Postconditions:
  - Returns a list of exactly 129 tuples (128 note buckets + 1 overflow bucket)
  - Each note bucket contains aggregated amplitude values
  - Overflow bucket (index 128) accumulates amplitudes for frequencies exceeding maxNote

## Side Effects
- None

## Control Flow
```mermaid
flowchart TD
    A[Start find_notes] --> B[Initialize res=[0]*129]
    B --> C[Create empty Note instance]
    C --> D[Iterate freqTable entries]
    D --> E{freq > 0 AND ampl > 0?}
    E -- No --> F[Skip entry]
    E -- Yes --> G[Call _find_log_index(freq)]
    G --> H{f < maxNote?}
    H -- Yes --> I[res[f] += ampl]
    H -- No --> J[res[128] += ampl]
    F --> K[Next entry]
    I --> K
    J --> K
    K --> L[End iteration]
    L --> M[Build return list]
    M --> N[enumerate res]
    N --> O{x < 128?}
    O -- Yes --> P[Note().from_int(x)]
    O -- No --> Q[None]
    P --> R[Return list of (Note, Note) tuples]
    Q --> R
```

## Examples
```python
# Basic usage with frequency data
freq_data = [(440.0, 0.8), (880.0, 0.5), (220.0, 0.3)]
notes = find_notes(freq_data)
# Returns list of note-amplitude mappings

# With custom maximum note limit
freq_data = [(1000.0, 0.9), (2000.0, 0.7)]
notes = find_notes(freq_data, maxNote=50)
# Frequencies above 50th note are grouped in overflow bucket
```

## `mingus.extra.fft.data_from_file` · *function*

## Summary:
Extracts mono audio data from the first channel of a WAV file along with sampling metadata.

## Description:
This function reads audio data from a WAV file and extracts the first audio channel as a list of integer samples. It also retrieves the sampling rate and bit depth information from the file header. The function is designed to handle multi-channel audio files by returning only the first channel, making it suitable for processing mono audio data from stereo or multi-channel recordings.

## Args:
    file (str): Path to the WAV audio file to read. Must be a valid path to a WAV file with proper header information.

## Returns:
    tuple: A tuple containing:
        - channel1 (list[int]): List of integer audio sample values from the first channel
        - freq (int): Sampling rate of the audio file in Hz
        - bits (int): Bit depth of the audio samples (1, 2, or 4 bytes per sample)

## Raises:
    FileNotFoundError: When the specified file path does not exist or cannot be opened
    wave.Error: When the file is not a valid WAV file or has corrupted header information
    struct.error: When the binary data cannot be unpacked according to the expected format

## Constraints:
    Preconditions:
        - Input file must be a valid WAV audio file
        - File must be readable and accessible
        - File must contain valid audio frame data
    Postconditions:
        - The returned channel1 list contains integer values representing audio samples
        - The frequency and bit depth values correspond to the actual WAV file header information
        - The file handle is properly closed after reading

## Side Effects:
    - Opens and reads from a file on disk
    - May raise file system related exceptions if the file is inaccessible

## Control Flow:
```mermaid
flowchart TD
    A[Start data_from_file] --> B{Open WAV file}
    B --> C{Read all frames}
    C --> D{Get file metadata}
    D --> E{Unpack binary data}
    E --> F{Extract first channel}
    F --> G[Close file handle]
    G --> H[Return (channel1, freq, bits)]
```

## Examples:
```python
# Basic usage
try:
    channel_data, sample_rate, bit_depth = data_from_file("audio.wav")
    print(f"Sample rate: {sample_rate}Hz")
    print(f"Bit depth: {bit_depth} bits")
    print(f"Number of samples: {len(channel_data)}")
except FileNotFoundError:
    print("Audio file not found")
except wave.Error:
    print("Invalid WAV file format")
```

## `mingus.extra.fft.find_Note` · *function*

## Summary
Identifies the musical note with the highest amplitude from audio frequency analysis.

## Description
Determines the dominant musical note present in audio data by analyzing the frequency spectrum obtained through Fast Fourier Transform (FFT) and mapping frequency components to musical notes. This function serves as a high-level interface that orchestrates frequency analysis and note mapping to return the most prominent note in the audio signal.

The function first processes raw audio data into a frequency spectrum using `find_frequencies`, then converts those frequency-amplitude pairs into musical note representations using `find_notes`. Finally, it identifies and returns the note with the highest amplitude value.

This logic is extracted into its own function to provide a clean abstraction layer that encapsulates the entire audio-to-note conversion pipeline, making it reusable and testable while maintaining separation of concerns between frequency analysis and note mapping operations.

## Args
- data (array-like): Audio sample data points, typically representing amplitude values over time
- freq (int): Sampling frequency in Hz, defaults to 44100 (standard CD quality)
- bits (int): Audio bit depth parameter (currently unused in implementation), defaults to 16 bits

## Returns
- Note: The musical note object with the highest amplitude in the frequency spectrum. Returns the note with the strongest frequency component detected in the audio data.

## Raises
- None explicitly documented in the source code

## Constraints
- Preconditions:
  - data must be a sequence of numeric values representing audio samples
  - freq must be a positive integer representing sampling frequency
  - bits must be a positive integer representing bit depth (though currently unused)

- Postconditions:
  - Returns a Note object representing the dominant musical note
  - The returned note corresponds to the frequency component with maximum amplitude

## Side Effects
- None

## Control Flow
```mermaid
flowchart TD
    A[Start find_Note] --> B[Call find_frequencies(data, freq, bits)]
    B --> C[Call find_notes(result_from_find_frequencies)]
    C --> D[Sort notes by amplitude]
    D --> E[Return note with highest amplitude]
```

## Examples
```python
# Basic usage with default parameters
audio_samples = [0.1, 0.2, 0.3, 0.4, 0.3, 0.2, 0.1]
dominant_note = find_Note(audio_samples, 44100, 16)
# Returns the musical note with highest amplitude in the audio signal

# Usage with custom sampling rate
dominant_note = find_Note(audio_samples, 22050, 16)
# Processes audio at 22kHz sampling rate and returns dominant note
```

## `mingus.extra.fft.analyze_chunks` · *function*

## Summary
Processes audio data in chunks to identify the dominant musical note from each segment.

## Description
Analyzes audio data by dividing it into fixed-size chunks and determining the most prominent musical note in each chunk. This function serves as a core component in audio-to-music transcription systems, enabling the conversion of continuous audio signals into discrete musical note sequences.

The function operates by repeatedly processing chunks of audio data through a frequency analysis pipeline: first extracting frequency components using FFT, then mapping those frequencies to musical notes, and finally selecting the note with the highest amplitude as the representative note for that chunk.

## Args
- data (list[float]): Sequence of audio sample values representing amplitude over time
- freq (int): Sampling frequency in Hz, typically 44100 for CD-quality audio
- bits (int): Audio bit depth specification (currently unused in implementation)
- chunksize (int, optional): Size of audio chunks to process in samples. Defaults to 512

## Returns
- list[Note]: List of musical Note objects representing the dominant note from each chunk of audio data

## Raises
- None explicitly raised by this function

## Constraints
- Preconditions:
  - data must be a sequence of numeric values representing audio samples
  - freq must be a positive integer representing sampling frequency
  - bits must be a positive integer representing bit depth
  - chunksize must be a positive integer

- Postconditions:
  - Returns a list of Note objects with one note per processed chunk
  - Each returned note corresponds to the highest amplitude musical note detected in its respective chunk
  - The length of the returned list equals the number of complete chunks in the input data

## Side Effects
- None

## Control Flow
```mermaid
flowchart TD
    A[Start analyze_chunks] --> B[Initialize res = []]
    B --> C{data != []?}
    C -- No --> D[Return res]
    C -- Yes --> E[Take data[:chunksize]]
    E --> F[Call find_frequencies(data[:chunksize], freq, bits)]
    F --> G[Call find_notes(f)]
    G --> H[Sort notes by amplitude]
    H --> I[Select highest amplitude note]
    I --> J[Append note to res]
    J --> K[Remove processed chunk from data]
    K --> C
```

## Examples
```python
# Basic usage with audio data
audio_samples = [0.1, 0.2, 0.3, 0.4, 0.3, 0.2, 0.1] * 100  # Simulated audio
dominant_notes = analyze_chunks(audio_samples, freq=44100, bits=16)
# Returns list of Note objects representing dominant notes from each chunk

# Custom chunk size
notes_with_custom_chunks = analyze_chunks(audio_samples, freq=44100, bits=16, chunksize=1024)
# Processes audio in 1024-sample chunks instead of default 512
```

## `mingus.extra.fft.find_melody` · *function*

## Summary:
Identifies and groups consecutive musical notes from audio data, creating a melody representation with note duration tracking.

## Description:
Processes audio data from a WAV file to extract musical notes and group consecutive identical notes into sequences with duration counts. This function serves as the final step in the audio-to-music transcription pipeline, converting raw audio analysis results into a structured melody representation where each note is paired with its occurrence count.

The function leverages the complete audio processing chain: first reading audio data from a file, then analyzing it in chunks to identify dominant musical notes, and finally grouping consecutive identical notes while counting their occurrences. This approach enables the creation of melody sequences that preserve both pitch information and temporal patterns.

Known callers within the codebase:
- This function is likely called by higher-level audio processing or music transcription modules that require a note-duration representation of audio content
- It would typically be invoked as part of a larger pipeline for automatic music transcription or audio analysis

This logic is extracted into its own function rather than being inlined because it encapsulates the specific business logic of note grouping and duration counting, separating it from the audio file I/O and frequency analysis concerns handled by the supporting functions.

## Args:
- file (str, optional): Path to the WAV audio file to process. Defaults to "440_480_clean.wav"
- chunksize (int, optional): Size of audio chunks in samples for processing. Defaults to 512

## Returns:
- list[tuple[Note, int]]: List of tuples where each tuple contains:
  - Note: Musical Note object representing the dominant pitch in that time segment
  - int: Count of consecutive occurrences of that note

## Raises:
- FileNotFoundError: When the specified audio file cannot be found or accessed
- wave.Error: When the audio file is not a valid WAV format or has corrupted header information
- struct.error: When binary data in the audio file cannot be properly unpacked

## Constraints:
- Preconditions:
  - Input file must be a valid WAV audio file with proper header information
  - File must be readable and accessible
  - Audio data must contain valid sample values
- Postconditions:
  - Returns a list of note-duration pairs
  - Each note in the result corresponds to a dominant musical note from the audio
  - Duration counts represent consecutive occurrences of the same note

## Side Effects:
- Opens and reads from a file on disk
- May raise file system related exceptions if the file is inaccessible

## Control Flow:
```mermaid
flowchart TD
    A[Start find_melody] --> B[Call data_from_file(file)]
    B --> C{Extract data, freq, bits}
    C --> D[Call analyze_chunks(data, freq, bits, chunksize)]
    D --> E{Process chunks}
    E --> F[Initialize res = []]
    F --> G[For each note d from analyze_chunks]
    G --> H{res != []?}
    H -- No --> I[Append (d, 1) to res]
    H -- Yes --> J[res[-1][0] == d?]
    J -- Yes --> K[Increment res[-1][1] by 1]
    J -- No --> L[Append (d, 1) to res]
    L --> M[Continue to next chunk]
    I --> M
    K --> M
    M --> N{More chunks?}
    N -- Yes --> G
    N -- No --> O[Return [(x, freq) for (x, freq) in res]]
```

## Examples:
```python
# Basic usage with default parameters
melody = find_melody()
# Processes the default test audio file with 512-sample chunks

# Custom file and chunk size
melody = find_melody("my_audio.wav", chunksize=1024)
# Processes custom audio file with larger chunks

# Processing result interpretation
for note, count in melody:
    print(f"Note {note} occurs {count} times consecutively")
```

