# `fft.py`

## `mingus.extra.fft._find_log_index` · *function*

## Summary:
Finds the logarithmic index in a cached lookup table for a given frequency value using optimized binary search.

## Description:
This function performs an optimized binary search on a global logarithmic frequency cache (_log_cache) to find the appropriate index for a given frequency value. It implements a caching strategy using _last_asked to optimize performance for sequential access patterns, making it efficient for repeated frequency lookups in audio processing applications.

## Args:
    f (float): The frequency value to find the logarithmic index for. Must be greater than 0.

## Returns:
    int: The logarithmic index in the cache array. Returns 128 if the frequency is outside the valid range (greater than maximum cache value or less than or equal to zero).

## Raises:
    None explicitly raised, but may raise IndexError if _log_cache is not properly initialized or has fewer than 128 elements.

## Constraints:
    Preconditions:
        - _log_cache must be a globally defined list/array with at least 128 elements
        - _last_asked must be either None or a tuple of (index, frequency_value)  
        - f must be a positive number
    Postconditions:
        - Returns an integer index between 0 and 128 inclusive
        - _last_asked is updated to reflect the most recent successful lookup

## Side Effects:
    - Modifies the global variable _last_asked to cache the most recent lookup result
    - Accesses the global variable _log_cache for lookups

## Control Flow:
```mermaid
flowchart TD
    A[Start _find_log_index(f)] --> B{f <= 0 or f > _log_cache[127]}
    B -- Yes --> C[Return 128]
    B -- No --> D{Has _last_asked?}
    D -- No --> E[Set begin=0, end=128]
    D -- Yes --> F{f >= lastval}
    F -- No --> E
    F -- Yes --> G{f <= _log_cache[lastn]}
    G -- Yes --> H[Return lastn]
    G -- No --> I{f <= _log_cache[lastn+1]}
    I -- Yes --> J[Return lastn+1]
    I -- No --> K[Set begin=lastn]
    E --> L[While begin != end]
    L --> M{n = (begin + end) // 2}
    M --> N{cp < f <= c}
    N -- Yes --> O[Update _last_asked, Return n]
    N -- No --> P{f < c}
    P -- Yes --> Q[Set end = n]
    P -- No --> R[Set begin = n]
    Q --> L
    R --> L
    L --> S[Update _last_asked, Return begin]
```

## Examples:
    # Typical usage in audio processing context
    # Assuming _log_cache is properly initialized with logarithmic frequencies
    index = _find_log_index(440.0)  # Finds index for A4 note (440 Hz)
    # Returns the logarithmic index for 440 Hz in the frequency cache

## `mingus.extra.fft.find_frequencies` · *function*

## Summary:
Computes frequency spectrum analysis from audio data using Fast Fourier Transform.

## Description:
Transforms time-domain audio samples into frequency-domain representation, returning pairs of frequencies and their corresponding power magnitudes. This function implements a standard FFT-based spectral analysis algorithm commonly used in audio processing applications.

The function extracts the positive frequency components from the full FFT output, applies proper scaling factors, and returns a list of (frequency, magnitude) tuples that represent the audio signal's frequency content. It specifically processes only the unique frequency points (due to symmetry in real signals) and properly scales the power values.

## Args:
    data (array-like): Time-domain audio samples to analyze. Should be a sequence of numeric values representing amplitude over time.
    freq (int): Sampling frequency in Hertz. Defaults to 44100 (CD quality). Must be positive.
    bits (int): Audio bit depth. Defaults to 16. Currently unused in computation but may be used for future extensions.

## Returns:
    list[tuple[float, float]]: List of (frequency, magnitude) pairs where:
        - frequency: Frequency value in Hertz (0 to Nyquist frequency)
        - magnitude: Power magnitude at that frequency bin (non-negative real number)

## Raises:
    TypeError: If data contains non-numeric elements that cannot be processed by FFT.
    ValueError: If data is empty or contains invalid values that cause FFT computation to fail.

## Constraints:
    Preconditions:
        - data must be a sequence of numeric values
        - freq must be a positive integer
        - bits must be a positive integer
        
    Postconditions:
        - Returns a list of length ceil((len(data) + 1) / 2)
        - All returned frequencies are non-negative
        - All returned magnitudes are non-negative

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start find_frequencies] --> B[data length n = len(data)]
    B --> C[p = _fft(data)]
    C --> D[uniquePts = ceil((n+1)/2)]
    D --> E[p = scaled_power_calculation]
    E --> F[p[0] = p[0]/2]
    F --> G{is n even?}
    G -->|Yes| H[p[-1] = p[-1]/2]
    H --> I[s = freq/n]
    G -->|No| I
    I --> J[freqArray = arange(0, uniquePts*s, s)]
    J --> K[return zip(freqArray, p)]
```

## Examples:
```python
# Basic usage with sample data
audio_samples = [0.1, 0.2, 0.3, 0.2, 0.1]
frequencies = find_frequencies(audio_samples, freq=44100)
print(frequencies[:3])  # First few (frequency, magnitude) pairs

# With different sampling rate
high_quality_audio = [0.0]*1024
result = find_frequencies(high_quality_audio, freq=96000)

# Typical usage in audio analysis
import numpy as np
signal = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))  # 440Hz sine wave
spectrum = find_frequencies(signal, freq=44100)
max_freq, max_mag = max(spectrum, key=lambda x: x[1])
print(f"Peak frequency: {max_freq:.1f} Hz")
```

## `mingus.extra.fft.find_notes` · *function*

## Summary:
Maps frequency-amplitude pairs to musical notes by converting frequencies to MIDI note numbers and aggregating amplitudes.

## Description:
Processes a list of frequency-amplitude pairs to identify musical notes. For each valid frequency-amplitude pair, it converts the frequency to a logarithmic index, aggregates amplitudes by note, and returns a list mapping each note to its total amplitude. Frequencies exceeding the maximum note threshold are grouped under a special "overflow" entry.

## Args:
    freqTable (list[tuple[float, float]]): List of (frequency, amplitude) pairs to process. Frequency must be positive, amplitude must be positive.
    maxNote (int): Maximum MIDI note number to consider. Frequencies mapping to higher notes are aggregated under index 128. Defaults to 100.

## Returns:
    list[tuple[Note or None, Note]]: List of (note, note) pairs where:
        - First element is a Note object for valid MIDI note numbers (0-127) or None for overflow entries
        - Second element is a dummy Note object (always the same instance)
        - Each pair corresponds to a position in the result array

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
        - freqTable must be iterable containing (frequency, amplitude) tuples
        - Each frequency must be positive (> 0)
        - Each amplitude must be positive (> 0)
        - maxNote must be a non-negative integer
    Postconditions:
        - Returns a list of exactly 129 elements
        - Elements at indices 0-127 represent valid notes
        - Element at index 128 represents overflow notes
        - Amplitudes are summed for each note index

## Side Effects:
    - Creates Note instances internally
    - Uses global variables from _find_log_index function
    - May modify global state in _find_log_index

## Control Flow:
```mermaid
flowchart TD
    A[Start find_notes] --> B[Initialize res=[0]*129]
    B --> C[Create dummy Note n]
    C --> D[For each (freq, ampl) in freqTable]
    D --> E{freq > 0 and ampl > 0?}
    E -- No --> F[Skip to next pair]
    E -- Yes --> G[Call _find_log_index(freq)]
    G --> H{f < maxNote?}
    H -- Yes --> I[res[f] += ampl]
    H -- No --> J[res[128] += ampl]
    J --> K[End loop]
    K --> L[Return list comprehension]
    L --> M[For each (x,n) in enumerate(res)]
    M --> N{x < 128?}
    N -- Yes --> O[Note().from_int(x)]
    N -- No --> P[None]
    O --> Q[Return (Note, n) pairs]
```

## Examples:
    # Basic usage with frequency data
    freq_data = [(440.0, 0.8), (523.25, 0.6), (659.25, 0.4)]
    result = find_notes(freq_data)
    # Returns list of note-amplitude pairs for detected notes
    
    # With maximum note limit
    result = find_notes(freq_data, maxNote=80)
    # Notes above MIDI note 80 are grouped under overflow entry

## `mingus.extra.fft.data_from_file` · *function*

## Summary:
Extracts audio data from a WAV file and returns the first channel's samples along with audio metadata.

## Description:
This function reads audio data from a WAV file and processes it to extract the first audio channel's sample values. It also retrieves important audio metadata including sampling frequency and bit depth. The function is designed to handle multi-channel audio files by isolating the first channel, making it suitable for mono processing workflows.

## Args:
    file (str): Path to the WAV audio file to process.

## Returns:
    tuple: A tuple containing:
        - channel1 (list[int]): Sample values from the first audio channel
        - freq (int): Sampling rate in Hz
        - bits (int): Bit depth of the audio samples

## Raises:
    FileNotFoundError: If the specified file does not exist.
    wave.Error: If the file is not a valid WAV file or cannot be opened.

## Constraints:
    Precondition: The input file must be a valid WAV audio file with readable audio frames.
    Postcondition: The returned channel1 list contains integer sample values representing the first audio channel.

## Side Effects:
    - Opens and closes the specified file for reading
    - Reads entire audio data from disk into memory

## Control Flow:
```mermaid
flowchart TD
    A[Start data_from_file] --> B[Open WAV file in read mode]
    B --> C[Read all audio frames]
    C --> D[Get audio metadata (channels, freq, bits)]
    D --> E[Unpack binary data to integers]
    E --> F[Extract first channel samples]
    F --> G[Close file handle]
    G --> H[Return (channel1, freq, bits)]
```

## Examples:
    # Basic usage
    samples, sample_rate, bit_depth = data_from_file("audio.wav")
    
    # Processing audio data
    try:
        samples, sample_rate, bit_depth = data_from_file("music.wav")
        print(f"Sample rate: {sample_rate} Hz")
        print(f"Bit depth: {bit_depth} bits")
        print(f"Number of samples: {len(samples)}")
    except (FileNotFoundError, wave.Error) as e:
        print(f"Error reading audio file: {e}")

## `mingus.extra.fft.find_Note` · *function*

## Summary:
Identifies the dominant musical note from audio frequency data by analyzing spectral content and mapping frequencies to MIDI note numbers.

## Description:
This function serves as the primary interface for extracting musical note information from audio data. It takes raw audio samples, performs frequency analysis using FFT, identifies musical notes from the frequency spectrum, and returns the note with the highest amplitude. The function orchestrates two core processing steps: frequency domain transformation followed by note mapping and amplitude aggregation.

The function is designed to be used in audio analysis pipelines where identifying the primary musical note from a sound clip is required. It abstracts away the complexity of FFT processing and note mapping into a single, convenient interface.

## Args:
    data (array-like): Time-domain audio samples to analyze. Should be a sequence of numeric values representing amplitude over time.
    freq (int): Sampling frequency in Hertz. Defaults to 44100 (CD quality). Must be positive.
    bits (int): Audio bit depth. Defaults to 16. Currently unused in computation but may be used for future extensions.

## Returns:
    Note: The musical note with the highest amplitude in the analyzed frequency spectrum. Returns a Note object representing the dominant pitch.

## Raises:
    TypeError: If data contains non-numeric elements that cannot be processed by FFT.
    ValueError: If data is empty or contains invalid values that cause FFT computation to fail.

## Constraints:
    Preconditions:
        - data must be a sequence of numeric values
        - freq must be a positive integer
        - bits must be a positive integer
        
    Postconditions:
        - Returns a valid Note object with proper pitch and octave information
        - The returned note corresponds to the frequency with maximum amplitude in the spectrum

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start find_Note] --> B[Call find_frequencies(data, freq, bits)]
    B --> C[Process frequency data with find_notes]
    C --> D[Sort notes by amplitude]
    D --> E[Return note with highest amplitude]
```

## Examples:
    # Basic usage to identify dominant note in audio
    audio_samples = [0.1, 0.2, 0.3, 0.2, 0.1]
    dominant_note = find_Note(audio_samples, freq=44100, bits=16)
    print(dominant_note)  # Displays the identified musical note
    
    # Typical usage in audio analysis application
    import numpy as np
    # Generate a 440Hz sine wave (A4 note)
    signal = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
    identified_note = find_Note(signal, freq=44100, bits=16)
    # Returns Note object representing A4

## `mingus.extra.fft.analyze_chunks` · *function*

## Summary:
Analyzes audio data chunks to identify dominant musical notes by performing frequency analysis and note mapping.

## Description:
Processes audio data in fixed-size chunks using FFT-based frequency analysis to extract the most prominent musical note from each chunk. This function orchestrates the audio processing pipeline by repeatedly applying frequency detection and note mapping operations on successive data segments.

The function is designed to handle continuous audio streams by breaking them into manageable chunks and analyzing each segment independently. It serves as a bridge between raw audio data and musical note identification, enabling applications like real-time pitch detection or audio transcription systems.

## Args:
    data (list[float]): Time-domain audio samples to analyze. Should contain numeric values representing amplitude over time.
    freq (int): Sampling frequency in Hertz. Must be positive and typically corresponds to standard audio rates (e.g., 44100 Hz).
    bits (int): Audio bit depth. Currently unused but maintained for API consistency.
    chunksize (int): Size of each data chunk to process. Defaults to 512 samples. Must be positive.

## Returns:
    list[Note]: List of Note objects representing the dominant musical note detected in each chunk. Empty list if input data is empty.

## Raises:
    TypeError: If data contains non-numeric elements that cannot be processed by underlying FFT functions.
    ValueError: If data is empty or contains invalid values that cause FFT computation to fail.

## Constraints:
    Preconditions:
        - data must be a sequence of numeric values
        - freq must be a positive integer
        - bits must be a positive integer
        - chunksize must be a positive integer
    Postconditions:
        - Returns a list with one Note per chunk processed
        - Each Note object represents a valid musical note
        - Empty input data results in empty output list

## Side Effects:
    - Calls external functions find_frequencies and find_notes
    - Creates Note objects during processing
    - May access global variables through find_notes dependency

## Control Flow:
```mermaid
flowchart TD
    A[Start analyze_chunks] --> B[Initialize res = []]
    B --> C{data != []?}
    C -- No --> D[Return res]
    C -- Yes --> E[Take data[:chunksize]]
    E --> F[Call find_frequencies(data[:chunksize], freq, bits)]
    F --> G[Call find_notes(f)]
    G --> H[Sort by amplitude (descending)]
    H --> I[Get highest amplitude note]
    I --> J[Append to res]
    J --> K[Remove processed chunk from data]
    K --> C
```

## Examples:
    # Basic usage with audio data
    audio_samples = [0.1, 0.2, 0.3, 0.2, 0.1] * 100  # 500 samples
    notes = analyze_chunks(audio_samples, freq=44100, bits=16)
    print(f"Detected {len(notes)} notes from audio chunks")
    
    # Processing with custom chunk size
    custom_chunks = analyze_chunks(audio_samples, freq=44100, bits=16, chunksize=256)
    print(f"Processing with {len(custom_chunks)} chunks of 256 samples each")

## `mingus.extra.fft.find_melody` · *function*

## Summary:
Identifies and groups consecutive musical notes from audio data by analyzing audio chunks and detecting dominant pitches.

## Description:
Processes audio data from a WAV file to detect musical notes and group consecutive occurrences of the same note. This function serves as the main interface for melody extraction from audio files, combining file reading, chunked audio analysis, and note grouping logic into a single cohesive operation.

The function breaks audio into chunks, identifies the dominant musical note in each chunk using frequency analysis, and groups consecutive identical notes together with their duration. The result represents a simplified musical timeline where each entry contains a note and how many consecutive chunks it appeared in.

## Args:
    file (str): Path to the WAV audio file to process. Defaults to "440_480_clean.wav".
    chunksize (int): Size of audio chunks to process in samples. Defaults to 512.

## Returns:
    list[tuple[Note, int]]: List of tuples where each tuple contains:
        - Note: The musical note detected in the chunk
        - int: Sampling frequency in Hz (not duration as previously described)

## Raises:
    FileNotFoundError: If the specified audio file does not exist.
    wave.Error: If the file is not a valid WAV file or cannot be opened.
    TypeError: If audio data contains non-numeric elements that cannot be processed.
    ValueError: If audio data is empty or contains invalid values causing FFT computation to fail.

## Constraints:
    Preconditions:
        - Input file must be a valid WAV audio file
        - Audio data must contain valid numeric sample values
        - chunksize must be a positive integer
    Postconditions:
        - Returns a list of note-frequency pairs
        - Each note in the result is a valid Note object
        - Consecutive identical notes are grouped together with cumulative count

## Side Effects:
    - Opens and reads audio file from disk
    - Processes audio data in memory
    - Creates Note objects during analysis
    - May access external functions for audio processing

## Control Flow:
```mermaid
flowchart TD
    A[Start find_melody] --> B[Call data_from_file(file)]
    B --> C[Unpack (data, freq, bits)]
    C --> D[Initialize res = []]
    D --> E[Iterate through analyze_chunks(data, freq, bits, chunksize)]
    E --> F{res != []?}
    F -- No --> G[Append (d, 1) to res]
    F -- Yes --> H{res[-1][0] == d?}
    H -- Yes --> I[Increment res[-1][1] by 1]
    H -- No --> J[Append (d, 1) to res]
    J --> K[Continue loop]
    G --> K
    I --> K
    K --> L[Return [(x, freq) for (x, freq) in res]]
```

## Examples:
    # Basic usage with default parameters
    melody = find_melody()
    print(f"Found {len(melody)} distinct notes in melody")
    
    # Process custom audio file with different chunk size
    custom_melody = find_melody("my_audio.wav", chunksize=1024)
    for note, frequency in custom_melody:
        print(f"Note {note} detected at {frequency} Hz")
```

