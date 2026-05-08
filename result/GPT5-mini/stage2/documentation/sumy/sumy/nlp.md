# `sumy.nlp`

## Tree:
nlp/
├── stemmers/
└── tokenizers.py

## Role:
Provide language-specific sentence- and word-tokenization primitives and a language-aware Tokenizer façade that composes those primitives for use by higher-level NLP pipelines (e.g., summarizers, extractors, preprocessing).

## Description:
- Where/when used:
  - Used during preprocessing, tokenization, and feature-extraction stages of the repository's NLP pipeline.
  - Primary consumers: summarizers, extractors, and any components that construct Tokenizer(language) and call to_sentences(...) and to_words(...).

- Why grouped separately:
  - Cohesion: this module centralizes tokenization strategies and optional third-party adapters so the rest of the codebase can request language-appropriate tokenization through a stable API without inlining dependency logic.
  - Layer boundary: it implements the tokenization layer that sits below summarization logic and above language-specific stemmers (nlp/stemmers/).

- Note about stemmers:
  - The stemmers/ subpackage contains language stemmers used downstream. See the nlp/stemmers module documentation for those components.

## Components:
Public classes and main callable signatures (one-line role each). For full behavior and edge cases, consult the component-level docs.

- Tokenizer(language: str)
  - Facade that selects sentence and word tokenizers for a language and exposes to_sentences(paragraph) and to_words(sentence).

- Tokenizer.language -> str
  - Read-only property returning the normalized language configured for the Tokenizer.

- Tokenizer.to_sentences(paragraph: str) -> tuple[str, ...]
  - Split paragraph into a tuple of sentence strings (whitespace-trimmed). Uses a special-case tokenizer or an NLTK Punkt tokenizer depending on language.

- Tokenizer.to_words(sentence: str) -> tuple[str, ...]
  - Tokenize a sentence using the configured word tokenizer and return a tuple of tokens that pass the Tokenizer's word predicate.

- Tokenizer._get_sentence_tokenizer(language: str) -> object
  - Helper selecting a special-case tokenizer or loading an NLTK Punkt tokenizer.

- Tokenizer._get_word_tokenizer(language: str) -> object
  - Helper returning a language-specific word tokenizer or a DefaultWordTokenizer fallback.

- Tokenizer._is_word(word: str) -> bool
  - Static predicate using the class word regex to filter token strings.

- DefaultWordTokenizer()
  - Stateless adapter delegating to nltk.word_tokenize(text) and returning the list that NLTK produces.

- ArabicSentencesTokenizer()
  - Adapter: tokenize(text) delegates to pyarabic.araby.sentence_tokenize(text) (lazy import). Returns whatever pyarabic returns.

- ArabicWordTokenizer()
  - Adapter: tokenize(text) delegates to pyarabic.araby.tokenize(text) (lazy import). Returns whatever pyarabic returns.

- ChineseWordTokenizer()
  - Adapter: tokenize(text) delegates to jieba.cut(text) (lazy import). Returns an iterable of token strings (caller often materializes into a list).

- GreekSentencesTokenizer
  - tokenize(text) -> list[str]: calls nltk.sent_tokenize(text, language='greek') then further splits on semicolon-like punctuation; returns a list of trimmed sentence fragments.

- HebrewWordTokenizer
  - tokenize(text) -> list[str]: removes ASCII punctuation, calls hebrew_tokenizer.tokenize, and returns only tokens classified as Hebrew groups.

- JapaneseWordTokenizer()
  - tokenize(text) -> sequence[str]: instantiates tinysegmenter.TinySegmenter() and returns its tokenize(text) result.

- KoreanSentencesTokenizer()
  - tokenize(text) -> list[str]: delegates to konlpy.tag.Kkma.sentences(text) (lazy import) and returns the resulting list of sentence strings.

- KoreanWordTokenizer()
  - tokenize(text) -> list[str]: delegates to konlpy.tag.Kkma.nouns(text) (lazy import) and returns the list of nouns.

Mermaid dependency graph:
graph TD
    Tokenizer -->|uses| SentenceTokenizers[Sentence tokenizers (special-case or NLTK Punkt)]
    Tokenizer -->|uses| WordTokenizers[Word tokenizers (Default or language-specific)]
    SentenceTokenizers --> Greek[GreekSentencesTokenizer (nltk)]
    SentenceTokenizers --> KoreanS[KoreanSentencesTokenizer (konlpy)]
    SentenceTokenizers --> ArabicS[ArabicSentencesTokenizer (pyarabic)]
    WordTokenizers --> Default[DefaultWordTokenizer (nltk)]
    WordTokenizers --> Chinese[ChineseWordTokenizer (jieba)]
    WordTokenizers --> Japanese[JapaneseWordTokenizer (tinysegmenter)]
    WordTokenizers --> ArabicW[ArabicWordTokenizer (pyarabic)]
    WordTokenizers --> Hebrew[HebrewWordTokenizer (hebrew_tokenizer)]
    WordTokenizers --> KoreanW[KoreanWordTokenizer (konlpy)]

## Public API:
(exported classes and expected signatures; callers rely on these interfaces)

- Tokenizer(language: str)
  - Create per-language tokenizer. Usage:
      tokenizer = Tokenizer("english")
      sentences = tokenizer.to_sentences(paragraph)   # tuple[str, ...]
      words = tokenizer.to_words(sentence)           # tuple[str, ...]
  - Note: constructing a Tokenizer for languages that use NLTK Punkt requires the appropriate punkt resource (nltk_data/tokenizers/punkt/<language>.pickle); if missing or corrupt, construction raises LookupError.

- DefaultWordTokenizer()
  - tokenize(text: str) -> list[str]
  - Description: delegates to nltk.word_tokenize and returns the list NLTK produces. Exceptions from nltk.word_tokenize (e.g., LookupError for missing resources) propagate to the caller.

- ArabicSentencesTokenizer
  - tokenize(text: str) -> object
  - Description: delegates to pyarabic.araby.sentence_tokenize; if pyarabic is missing the method raises ValueError with an installation hint.

- ArabicWordTokenizer
  - tokenize(text: str) -> object
  - Description: delegates to pyarabic.araby.tokenize; raises ValueError if pyarabic missing.

- ChineseWordTokenizer
  - tokenize(text: str) -> iterable[str]
  - Description: delegates to jieba.cut. Raises ValueError if jieba missing. The returned iterable is typically lazy; callers may convert to list().

- GreekSentencesTokenizer
  - tokenize(text: str) -> list[str]
  - Description: uses nltk.sent_tokenize(language='greek') then splits on semicolon-like punctuation; requires NLTK punkt Greek resources.

- HebrewWordTokenizer
  - tokenize(text: str) -> list[str]
  - Description: removes ASCII punctuation, calls hebrew_tokenizer.tokenize, filters tokens to Hebrew groups. Raises ValueError if hebrew_tokenizer missing.

- JapaneseWordTokenizer
  - tokenize(text: str) -> sequence[str]
  - Description: constructs tinysegmenter.TinySegmenter and calls its tokenize method. Raises ValueError if tinysegmenter missing.

- KoreanSentencesTokenizer
  - tokenize(text: str) -> list[str]
  - Description: delegates to konlpy.tag.Kkma.sentences(text). Raises ValueError if konlpy missing.

- KoreanWordTokenizer
  - tokenize(text: str) -> list[str]
  - Description: delegates to konlpy.tag.Kkma.nouns(text). Raises ValueError if konlpy missing.

- nlp.stemmers (submodule)
  - See nlp/stemmers documentation for stemmers and their public API.

## Dependencies:
- Internal:
  - nlp.stemmers: stemmers used later in pipelines (documented separately).
  - utils helpers (language normalization and to_unicode conversion) used inside Tokenizer (normalize_language, to_unicode). See utils module docs for those helpers.

- External (third-party) and why:
  - nltk: used by DefaultWordTokenizer (nltk.word_tokenize), by GreekSentencesTokenizer (nltk.sent_tokenize with language='greek'), and by Tokenizer when loading Punkt resources via nltk.data.load. NLTK punkt models are required for non-special languages.
  - jieba: Chinese segmentation (ChineseWordTokenizer). Optional; imported lazily inside the adapter.
  - pyarabic: Arabic sentence/word tokenization adapters (ArabicSentencesTokenizer, ArabicWordTokenizer). Optional; imported lazily inside adapters.
  - tinysegmenter: Japanese tokenization (JapaneseWordTokenizer). Optional; imported lazily inside adapter.
  - hebrew_tokenizer: Hebrew tokenization and Groups constants used by HebrewWordTokenizer. Optional; imported lazily.
  - konlpy: Korean sentence and noun extraction (KoreanSentencesTokenizer, KoreanWordTokenizer). Optional; imported lazily.
  - zipfile: indirectly relevant via nltk.data.load — corrupt pickles may surface zipfile.BadZipfile which Tokenizer handles by re-raising LookupError with context.

Notes:
- Optional dependencies are intentionally imported at call-time by adapters so they remain optional at package install time. When missing, adapters raise ValueError with an explicit pip install hint; callers can catch that to provide fallbacks.

## Constraints:
- Initialization prerequisites:
  - Tokenizer for Punkt-based languages: requires the corresponding NLTK punkt pickle present and readable. Missing/corrupt data causes LookupError on tokenizer initialization.

- Thread-safety:
  - Tokenizer.to_sentences may mutate an underlying tokenizer's _params.abbrev_types when present; sharing a single Tokenizer instance across threads may cause races updating that set. To avoid races, either create per-thread Tokenizer instances or serialize access.
  - Underlying third-party libraries (nltk, konlpy, jieba, tinysegmenter, hebrew_tokenizer) have their own thread-safety characteristics; assume they are not guaranteed thread-safe unless their docs state otherwise.

- Performance / ordering:
  - Some adapters instantiate analyzers per call (e.g., JapaneseWordTokenizer constructs TinySegmenter() each time; Korean adapters create Kkma() per call). For high-throughput usage, callers should consider reusing underlying analyzer instances to reduce allocation and import overhead.

- Input expectations:
  - Most tokenizers expect Unicode/text (str). Passing non-text objects may raise TypeError or AttributeError (e.g., HebrewWordTokenizer calls str.translate on input). Convert or validate inputs before calling tokenizers.
  - Tokenizers do not perform language detection; callers must select the correct Tokenizer(language).

- Error handling:
  - Optional dependency missing -> adapters raise ValueError with a pip-install hint.
  - Underlying library errors (TypeError, ValueError, LookupError from NLTK, konlpy runtime errors) are propagated to the caller.

Refer to individual component documentation (e.g., ArabicSentencesTokenizer, HebrewWordTokenizer, Tokenizer) for exact exception messages, per-method parameter and return types, and edge-case behavior.

---

## Files

- [`tokenizers.py`](nlp/tokenizers.md)

