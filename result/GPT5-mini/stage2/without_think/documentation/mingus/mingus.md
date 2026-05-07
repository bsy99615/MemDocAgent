# `mingus`

## Tree:
mingus/
├── mingus/                 - Top-level package: groups domain, theory, extras, and MIDI subsystems
│   ├── containers/         - In-memory domain models (notes, bars, tracks, compositions) and domain exceptions
│   ├── core/               - Theory utilities, parsers, and analysis helpers
│   ├── extra/              - Optional utilities and format adapters (extension area)
│   └── midi/               - MIDI I/O: message/file generation, parsing, and runtime adapters
├── mingus_examples/        - Examples demonstrating Pygame + Fluidsynth integration
│   ├── pygame-drum/
│   │   └── pygame-drum.py  - Drum-pad demo: asset loader and play_note helper
│   └── pygame-piano/
│       └── pygame-piano.py - Interactive piano demo: visuals + play_note helper
└── scripts/
    └── api_doc_generator.py - Developer CLI/tool: reflectively generate per-module API docs (Documize class)

## Purpose:
This repository provides a small music-processing library plus supporting artifacts and developer tooling:
- A library of canonical musical domain models and pure theory helpers intended to be imported and reused by applications and tools.
- Runnable example programs demonstrating visuals and audio playback (Pygame + Fluidsynth) that illustrate integration patterns.
- A developer-focused CLI tool (scripts/api_doc_generator.py) whose primary usage is to generate API reference pages for the codebase via runtime reflection.

Why this matters:
- It offers a lightweight, opinionated set of domain types and musical algorithms useful for composition tools, editors, analysis scripts, and export/playback adapters.
- The examples accelerate learning and prototyping by showing end-to-end wiring of domain objects into interactive visuals and audio.
- The documentation generator simplifies producing per-module reference pages for maintainers.

Target users and scenarios:
- Application developers building music editors, converters, or playback tools (import mingus and its subpackages).
- Developers learning integrations using the examples (run example scripts directly).
- Repository maintainers and documentation authors who run scripts/api_doc_generator.py to emit API reference documents.

Position in the broader ecosystem:
- Primary role: library + examples for application developers.
- Secondary (developer tooling) role: scripts/api_doc_generator.py is primarily a CLI/documentation generator used by maintainers to produce reference documents; it is not required for runtime use of the core library.

## Architecture:
High-level flowchart (end-to-end data flow)
flowchart TD
  UserApp[User application / scripts] -->|import| MingusPkg[mingus package]
  MingusPkg --> Containers[mingus.containers\n(domain objects)]
  MingusPkg --> Core[mingus.core\n(theory & algorithms)]
  MingusPkg --> Extra[mingus.extra\n(optional helpers)]
  MingusPkg --> Midi[mingus.midi\n(MIDI adapters/export)]
  Containers --> Midi
  Core --> Midi
  UserApp -->|run example| Examples[mingus_examples\n(Pygame + Fluidsynth)]
  Examples -->|use| Containers
  Examples -->|play| Fluidsynth[fluidsynth (external)]
  Examples -->|render| Pygame[pygame (external)]
  scripts_api[ scripts/api_doc_generator.py ] -->|reflect| MingusPkg

Key abstractions and architectural patterns:
- Layered separation: domain (containers), theory (core), and adapters/IO (midi, extra).
- Extension area: mingus.extra holds optional adapters and utilities.
- Developer tooling: scripts/api_doc_generator.py implements a reflection-based doc-generation pipeline (Documize) intended for maintainers.
- Design goals: small, stable core APIs; clear adapter boundaries; examples as recipes.

## Entry Points:
- Importable APIs:
  - import mingus
    - Exposes subpackages: mingus.containers, mingus.core, mingus.extra, mingus.midi.
    - Audience: application developers who need domain models and theory helpers. Consult subpackage docs for exact signatures.

- Example scripts (runnable modules):
  - mingus_examples/pygame-piano/pygame-piano.py
    - Exports: load_img(name) and play_note(note) helpers for demo usage.
    - Requirements: initialized pygame display and configured Fluidsynth; when imported, certain module-level globals must be prepared by the caller.
    - Audience: developers exploring visual/audio integration or running the demo interactively.
  - mingus_examples/pygame-drum/pygame-drum.py
    - Exports: load_img(name) and play_note(note); optional recording controlled via module-level globals.
    - Requirements: same runtime initialization (pygame and Fluidsynth).
    - Audience: demo consumers and integration examples.

- CLI / developer tool (primary usage for this module):
  - scripts/api_doc_generator.py (Documize and main)
    - Exposes:
      - Documize(module_string: str = ''): programmatic API to reflectively assemble a module RST/wiki string (use output_wiki()).
      - generate_package_wikidocs(...): CLI helper that writes per-module docs to sys.argv[1] (output directory).
      - main(): validates args and invokes the generator for canonical packages.
    - Primary audience: maintainers and documentation authors. Note: Documize.set_module uses eval(); pass only trusted module expressions.

## Core Features:
- Domain types and in-memory containers
  - One-line: Canonical musical objects and mutable containers (Note, Bar, Track, Composition).
  - Implemented in: mingus.containers
- Theory and parsing helpers
  - One-line: Parsers, chord inference, and musical arithmetic utilities used across the library and examples.
  - Implemented in: mingus.core
- MIDI generation and adapters
  - One-line: Convert domain models to MIDI messages/files and provide runtime MIDI I/O adapters.
  - Implemented in: mingus.midi
- Optional format adapters / utilities
  - One-line: Non-essential helpers and format bridges suitable for experimental features or community extension.
  - Implemented in: mingus.extra
- Interactive Pygame + Fluidsynth examples
  - One-line: Small demos showing how to render keyboard/drum UI and play audio from Mingus Note objects.
  - Implemented in: mingus_examples/pygame-piano, mingus_examples/pygame-drum
- Reflection-based API documentation generator (developer tool)
  - One-line: Programmatic and CLI tooling to produce module reference pages via runtime introspection.
  - Implemented in: scripts/api_doc_generator.py (Documize)

## Dependencies:
Key external dependencies and roles:
- pygame
  - Role: Windowing, rendering, image loading, fonts, and event loop used by the example programs (mingus_examples).
  - Scope: example-only.
- fluidsynth (Python bindings)
  - Role: play_Note API used to produce audio in the examples.
  - Scope: example-only.
- Standard library modules used by scripts/api_doc_generator.py:
  - sys, os, inspect, types, builtins.eval
  - Role: CLI handling, file I/O, reflection, signature/docstring extraction for documentation generation.
- MIDI backend libraries (adapter-specific)
  - Role: mingus.midi may integrate with third-party MIDI libraries for platform-specific I/O. Consult mingus.midi docs for concrete dependencies.

Version constraints and compatibility:
- No explicit version pins are present here; module-level documentation or top-level packaging manifests should be consulted for exact Python and dependency compatibility requirements.

## Configuration:
- Runtime initialization:
  - Examples require pygame.display to be initialized before calling load_img for best Surface conversions.
  - Fluidsynth must be initialized and channels configured before play_note.
  - scripts/api_doc_generator.generate_package_wikidocs expects sys.argv[1] to be the output directory; main() validates this.
- Security/configuration notes:
  - Documize.set_module uses eval(); avoid passing untrusted strings. Prefer importlib.import_module or passing module objects in reimplementations.

## Extension Points:
- mingus.extra
  - Intended location for optional adapters, format converters, and non-core utilities to keep core package minimal.
- MIDI adapters
  - Implement backend-specific adapter modules under mingus.midi that conform to the midi adapter interface; keep adapter code separate to avoid coupling core models to platform-specific I/O.
- Examples as integration guides
  - Use mingus_examples as recipes for rendering and audio; copy/adapt play_note/load_img helpers for new front-ends.
- Documentation generator
  - Documize is a programmatic extension point for documentation formatting; you can swap its evaluation/resolution strategy (avoid eval) or change output format (Markdown, RST, wiki) as needed.

## Links to module-level documentation (do not duplicate):
- mingus (top-level package): high-level grouping and public API pointers (containers, core, extra, midi)
- mingus.containers: domain types and exceptions
- mingus.core: theory, parsing, and analysis helpers
- mingus.extra: optional helpers and adapters
- mingus.midi: MIDI generation and runtime adapters
- mingus_examples.pygame-drum: demo helpers and recording contract
- mingus_examples.pygame-piano: visual + audio demo and required module-level globals
- scripts.api_doc_generator.Documize: reflection-based documentation generator and its helpers (primary CLI usage)

Notes for implementers:
- Recreate domain types and invariants in mingus.containers first, then implement stateless theory helpers in mingus.core. Implement adapter layers (mingus.midi, mingus.extra) afterward. Use the examples as integration tests. For documentation generation, prefer safe module resolution over eval() when reimplementing generate_package_wikidocs and Documize.set_module.

---

## Modules

- [`mingus`](mingus.md)
- [`mingus/containers`](mingus/containers.md)
- [`mingus/core`](mingus/core.md)
- [`mingus/extra`](mingus/extra.md)
- [`mingus/midi`](mingus/midi.md)
- [`mingus_examples`](mingus_examples.md)
- [`mingus_examples/pygame-drum`](mingus_examples/pygame-drum.md)
- [`mingus_examples/pygame-piano`](mingus_examples/pygame-piano.md)
- [`scripts`](scripts.md)

