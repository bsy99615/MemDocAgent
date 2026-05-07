# `sumy.parsers`

## Tree:
parsers/
├── html.py
├── parser.py
└── plaintext.py

## Role:
Provides document parsing capabilities for HTML and plain text formats to produce structured document models for text summarization.

## Description:
The parsers module offers specialized document parsers that transform content from different input formats into structured document models suitable for text analysis and summarization. It contains two main parser implementations: HtmlParser for processing HTML documents and PlaintextParser for handling plain text content.

The HtmlParser leverages the breadability library to extract readable content from HTML markup and organizes it into paragraphs and sentences while preserving semantic information from HTML tags. The PlaintextParser processes plain text by identifying headings (uppercase lines), separating paragraphs (empty lines), and converting remaining content into structured sentences.

Both parsers inherit from a common DocumentParser base class that provides shared tokenization functionality for sentence and word processing. The parsers are designed to be instantiated through factory methods rather than direct construction, ensuring proper handling of different input sources.

## Components:
- HtmlParser: Parses HTML documents using breadability library to extract readable content and identify semantic elements
- PlaintextParser: Processes plain text by identifying headings, paragraphs, and organizing content into structured document models
- DocumentParser: Base class providing shared tokenization functionality for sentence and word processing

## Public API:
- HtmlParser.from_string(html_content: str, url: str, tokenizer): Creates parser from HTML string
- HtmlParser.from_file(file_path: str, url: str, tokenizer): Creates parser from HTML file
- HtmlParser.from_url(url: str, tokenizer): Creates parser from HTML URL
- PlaintextParser.from_string(text: str, tokenizer): Creates parser from text string
- PlaintextParser.from_file(file_path: str, tokenizer): Creates parser from text file
- DocumentParser(tokenizer): Base class constructor for tokenization

## Dependencies:
- Internal: sumy.nlp.tokenizers.Tokenizer (for sentence/word tokenization)
- External: breadability (for HTML content extraction), requests (for URL fetching)

## Constraints:
- All parsers must be instantiated through factory methods to ensure proper initialization
- Tokenizer objects must implement to_sentences() and to_words() methods
- HtmlParser requires breadability library for HTML processing
- PlaintextParser requires proper text encoding handling

---

## Files

- [`html.py`](parsers/html.md)
- [`parser.py`](parsers/parser.md)
- [`plaintext.py`](parsers/plaintext.md)

