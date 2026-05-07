# `mingus.containers`

## Tree:
containers/
├── bar.py
├── composition.py
├── instrument.py
├── mt_exceptions.py
├── note.py
├── note_container.py
├── suite.py
└── track.py

## Role:
Provide in-memory container primitives that model musical structures (Notes, NoteContainers, Bars, Tracks, Compositions and Suites) and instrument metadata/exceptions; this module owns the data/layout and mutation semantics for musical content used by higher-level processing and export logic.

## Description:
- Where and when this module is used:
  - Primary consumers are application logic that assembles, edits, analyzes, or exports music: composition builders, track renderers, chord/progression analyzers, and playback/export pipelines in the repository.
  - Examples of direct callers (by conceptual role): composition editors build Composition and Track objects; chord/progression analyzers ask Bars/NoteContainers for chord names; transport/export code iterates Track.get_notes/backing Bars for output.

- Why these components are grouped:
  - Cohesion principle: they all model musical containers and their immediate behaviors (holding notes, placing notes into bars, grouping bars into tracks, grouping tracks into compositions/suites).
  - Layer boundary: containers provide mutable, in-memory domain objects and small batch operations (transpose, augment, diminish) but delegate analysis/parsing/formatting to core modules (chords, progressions, intervals, notes). The module is intentionally pure-data + domain mutations (no IO).

## Components:
(Only public classes, exceptions and top-level functions exported by the module tree are listed; see each file for detailed component-level doc.)

- bar.Bar(key: str|keys.Key='C', meter: tuple[int,int]=(4,4))
  - Container for entries within a measure; manages placements, meter, current beat, and bar-level operations (place_notes, place_rest, place_notes_at, remove_last_entry, determine_chords, determine_progression, augment/diminish/transpose, empty, set_meter, etc.)
  - Important explicit behavior: empty() resets the Bar to an initial empty state by assigning a new empty list to self.bar and setting self.current_beat = 0.0; it returns the new (empty) list object. This is a destructive reset of the bar instance's storage (the previous list object, if referenced elsewhere, will not be modified by this call).

- composition.Composition()
  - Holds ordered collection of Track-like objects and composition metadata (title, author, selected_tracks); supports add_track, add_note (dispatch to tracks), indexing and simple metadata API.

- instrument.Instrument()
  - Metadata for playable range and basic range checks (note_in_range, can_play_notes, set_range); subclasses provide instrument-specific constraints.
  - Subclasses:
    - instrument.Guitar() : Instrument specialization with six-note maximum for chords and default range E3–E7.
    - instrument.MidiInstrument(name: str="") : MIDI preset instrument metadata (names, default range).
    - instrument.MidiPercussionInstrument() : Provides percussion mapping and accessor methods returning Note objects for GM percussion.
    - instrument.Piano() : Instrument specialization with default piano range.

- mt_exceptions.*
  - MeterFormatError(Exception): raised when meter validation fails
  - NoteFormatError(Exception): raised for invalid note format
  - UnexpectedObjectError(Exception): raised when an API receives an incompatible object
  - InstrumentRangeError(Exception): raised when an instrument cannot play requested notes

- note.Note(name: str|int|NoteLike='C', octave: int=4, dynamics: dict=None, velocity=None, channel=None)
  - Small, mutable pitch object with parsing, int() conversion to semitone number, transposition, octave adjustments, dynamics (velocity/channel), and conversion utilities (to_hertz, from_hertz, shorthand forms).

- note_container.NoteContainer(notes=None)
  - Holds a deduplicated, sorted collection of Note objects; supports add_note(s), remove_note(s), chord/interval/progression factories (from_chord_shorthand, from_interval_shorthand, from_progression_shorthand), batch ops (augment, diminish, transpose), and analyzers (determine, get_note_names, consonance predicates).
  - Implementation note: add_notes accepts many input shapes and delegates per-element normalization and insertion to add_note; callers should read add_note if they need exact per-element normalization rules.

- suite.Suite()
  - A lightweight collection of Composition-like objects with suite-level metadata (title, author, description). Note: class-level mutable default for compositions exists (see Constraints).

- track.Track(instrument=None)
  - Sequence of Bar objects (self.bars); higher-level orchestration for adding bars or notes, expanding chords into notes (from_chords), per-track transformations (transpose/augment/diminish), tuning support, and iteration across notes (get_notes).
  - Implementation note: add_notes performs track-level orchestration — it validates against an attached instrument (raising InstrumentRangeError when the instrument refuses the notes), ensures a target Bar exists (appending new Bar objects when the track is empty or when the last bar reports full), then delegates placement to the Bar.place_notes method; the boolean result returned by Bar.place_notes (True/False) is returned to callers (True if placement succeeded, False if insufficient space). This orchestration does not call Bar.empty() on existing bars; empty() is a separate API used to reset a specific Bar instance.

Mermaid dependency graph (internal relationships):
  - Note and NoteContainer are foundational and used by Bar and Track.
  - Bar contains NoteContainer(s) or Note references and exposes placement/detection operations.
  - Track contains Bars and delegates per-bar placement and transformations.
  - Composition groups Tracks and delegates add_note to tracks.
  - Suite groups Compositions.
  - Instruments are consulted by Track.add_notes and Track.get_tuning.
  - mt_exceptions are used across components for domain-specific errors.

Mermaid (text):
graph LR
  Note --> NoteContainer
  NoteContainer --> Bar
  Bar --> Track
  Track --> Composition
  Composition --> Suite
  Track --> Instrument
  Instrument --> mt_exceptions
  NoteContainer --> mingus_core_chords[mingus.core.chords]
  Bar --> mingus_core_progressions[mingus.core.progressions]

## Public API:
(Primary types & methods that other modules call; signatures are abbreviated)

- Bar(key='C', meter=(4,4))
  - place_notes(notes, duration) -> bool
    - Convert input (NoteContainer | name-like | string | list | None) into a NoteContainer or rest, attempt to append at bar.current_beat; returns True on success, False if out-of-space (length != 0.0).
  - place_rest(duration) -> bool
  - place_notes_at(notes, at) -> None
  - remove_last_entry() -> float
  - is_full() -> bool
  - get_note_names() -> list[str]
  - determine_chords(shorthand=False) -> list[[position, chord_result]]
  - determine_progression(shorthand=False) -> list[[position, progression_result]]
  - transpose(interval, up=True) -> None
  - augment(), diminish()
  - empty() -> list
    - Explicit: clears the bar's internal storage and resets current_beat to 0.0; returns the new empty list assigned to self.bar.
  - set_meter(meter) -> None
  - __len__(), __getitem__(), __repr__()

- NoteContainer(notes=None)
  - add_note(note, octave=None, dynamics=None) -> list
  - add_notes(notes) -> list
    - Accepts multiple input shapes and delegates per-element normalization/insertion to add_note. See add_note for precise conversion and insertion semantics.
  - remove_note(note, octave=-1) -> list
  - remove_notes(notes) -> list
  - sort() -> None
  - transpose(interval, up=True) -> self
  - augment(), diminish()
  - from_chord_shorthand(shorthand, key='C') -> self
  - from_interval_shorthand(startnote, shorthand, up=True) -> self
  - from_progression_shorthand(shorthand, key='C') -> self | False
  - get_note_names() -> list[str]
  - determine(shorthand=False) -> chords.determine result
  - is_consonant(include_fourths=True), is_perfect_consonant(include_fourths=True), is_imperfect_consonant() -> bool

- Note(name='C', octave=4, dynamics=None, velocity=None, channel=None)
  - __int__() -> int
  - set_note(name, octave, dynamics=None) -> self
  - transpose(interval, up=True) -> None
  - from_int(int_value) -> self
  - from_hertz(hz, standard_pitch=440) -> self
  - to_hertz(standard_pitch=440) -> float
  - to_shorthand(), from_shorthand(shorthand) -> self
  - set_velocity(vel), set_channel(ch) -> None
  - augment(), diminish(), remove_redundant_accidentals(), octave_up(), octave_down()

- Track(instrument=None)
  - add_bar(bar) -> self
  - add_notes(note, duration=4) -> bool
    - Orchestrates instrument-range validation (raises InstrumentRangeError if an instrument rejects the notes), ensures a target Bar exists (appending new Bars when empty or when last bar is full), and delegates placement to Bar.place_notes; returns the boolean result from Bar.place_notes indicating success/failure for that placement. Note: this orchestration does not call Bar.empty() on existing bars.
  - from_chords(chords_iterable, duration=1) -> self
    - Converts chord descriptors into NoteContainer(s) (optionally using tuning.find_chord_fingering when a tuning is available) and places them sequentially into the track, splitting across bar boundaries when needed.
  - get_tuning() -> tuning_or_None
  - set_tuning(tuning) -> self
  - transpose(interval, up=True) -> self
  - augment(), diminish() -> self
  - get_notes() -> generator of (beat, duration, notes)
  - __len__(), __getitem__(), __setitem__(), __repr__()

- Composition()
  - add_track(track) -> None (validates presence of 'bars')
  - add_note(note) -> None (for each selected_tracks index: tracks[n] + note)
  - set_title(title, subtitle=""), set_author(author, email="")
  - empty(), reset()
  - __len__(), __getitem__(), __setitem__(), __repr__()

- Suite()
  - add_composition(composition) -> self (validates 'tracks' attribute)
  - set_title(title, subtitle=""), set_author(author, email="")
  - __len__(), __getitem__(), __setitem__(), __add__ operate on compositions

- Exceptions:
  - mt_exceptions.MeterFormatError
  - mt_exceptions.NoteFormatError
  - mt_exceptions.UnexpectedObjectError
  - mt_exceptions.InstrumentRangeError

Usage notes:
- Prefer public helpers (Track.add_notes, Bar.place_notes, NoteContainer.add_notes, Composition.add_track). NoteContainer.add_notes handles multiple input shapes but delegates per-element conversion and insertion to add_note — read add_note if you need exact per-element normalization rules.
- Track.add_notes is the high-level placement orchestrator: it validates against an attached instrument (raising InstrumentRangeError when the instrument refuses the notes), ensures the existence of a target Bar (appending new Bar objects when the track is empty or when the last bar reports full), and delegates actual insertion to Bar.place_notes — the boolean result from Bar.place_notes is returned to the caller. This orchestration does not call Bar.empty() on existing bars; empty() is used when a bar must be explicitly reset.

## Dependencies:
Internal imports (core modules used by containers; these implement parsing, chord/progression detection, and interval/value math):
- mingus.core.notes: note <-> int mappings, accidental helpers (used by Note.__int__, augment, diminish, remove_redundant_accidentals)
- mingus.core.intervals: interval parsing and transpose helpers (used by Note.transpose)
- mingus.core.chords: parse chord shorthands and determine chord names (used by NoteContainer.determine, from_chord_shorthand)
- mingus.core.progressions: progression detection (used by Bar.determine_progression)
- mingus.core.value: arithmetic helpers for splitting durations (used by Track.from_chords)

Internal container inter-dependencies:
- note.py ↔ note_container.py: NoteContainer constructs/manipulates Note instances.
- bar.py uses note_container.NoteContainer and Note for entries and delegates per-entry operations.
- track.py uses bar.Bar and instrument.Instrument for placement and range checks.
- composition.py and suite.py orchestrate Track and Composition respectively.

External third-party imports:
- six (six.string_types) used by Note and other constructors to detect strings.
- Standard library: math (log) for frequency conversion.

## Constraints:
- Mutability / Thread-safety:
  - No component in this module is thread-safe. All container operations mutate internal lists in place without locks. Concurrent modifications require external synchronization.
- Ordering / initialization requirements:
  - Bars store entries as [start_beat, duration, notes] (consumers assume this shape). Use Bar.place_notes / place_rest to maintain invariant.
  - set_meter must be used or the Bar must be constructed with a valid meter; meter (0,0) produces length == 0.0 and special "unbounded" behavior.
  - Track.add_notes may append new Bar() instances before attempting placement; a False return only indicates Bar.place_notes failed to place the requested event in the final target Bar.
- Representation pitfalls and invariants to respect:
  - Many classes rely on attribute naming conventions (.name/.octave/.notes/.bar/.bars/.tracks/.compositions). Use public APIs rather than mutating internals directly.
  - Beware class-level mutable defaults in Composition and Suite (tracks, compositions). For per-instance isolation, assign instance-scoped lists on creation (e.g., instance.compositions = []).
  - Bar entry shapes must be consistent; some historical methods expect nested formats — prefer the canonical [start, duration, notes] produced by place_notes.
- Error and exception semantics:
  - InstrumentRangeError: raised by Track.add_notes when an attached instrument's can_play_notes denies the note(s).
  - MeterFormatError: raised by Bar.set_meter for invalid denominators.
  - NoteFormatError and UnexpectedObjectError: raised by parsing/normalization helpers on malformed input.

## Reimplementation guidance (high level):
- Respect the single-responsibility split:
  - Note: parsing/formatting and numeric conversions.
  - NoteContainer: per-element normalization via add_note, collection dedup/sort, and chord/progression factories that call core parsers.
  - Bar: placement bookkeeping, meter/length management, and per-bar analysis.
  - Track: bar management, instrument checks, and high-level placement orchestration (ensuring bars exist and splitting across boundaries).
  - Composition/Suite: lightweight collections and metadata.
- Delegate parsing and analysis to core modules (notes, intervals, chords, progressions, value).
- Preserve explicit behaviors and edge cases described above (e.g., add_notes delegation to add_note, Track.add_notes appends bars and returns Bar.place_notes result, special handling of meter (0,0), and instrument-range enforcement).

---

## Files

- [`bar.py`](containers/bar.md)
- [`composition.py`](containers/composition.md)
- [`instrument.py`](containers/instrument.md)
- [`mt_exceptions.py`](containers/mt_exceptions.md)
- [`note.py`](containers/note.md)
- [`note_container.py`](containers/note_container.md)
- [`suite.py`](containers/suite.md)
- [`track.py`](containers/track.md)

