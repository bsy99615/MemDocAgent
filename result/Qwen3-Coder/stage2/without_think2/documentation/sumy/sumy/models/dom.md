# `sumy.models.dom`

## Tree:
dom/
├── _document.py
├── _paragraph.py
└── _sentence.py

## Role:
Provides a hierarchical document object model (DOM) for representing structured text documents composed of sentences, paragraphs, and full documents.

## Description:
The dom module implements a hierarchical document model that organizes text content into nested structures: sentences form paragraphs, paragraphs compose documents. This abstraction enables efficient processing of document structure while maintaining clear separation between content representation and analysis operations.

This module is primarily consumed by document processors, parsers, and summarization algorithms that need to traverse and analyze document structure. The design emphasizes immutability at the document and paragraph levels for the core structural data, with cached properties for efficient access to aggregated content.

## Components:
- ObjectDocumentModel: Main document container aggregating paragraphs
- Paragraph: Container for sentences within a document section
- Sentence: Atomic text unit with tokenization capabilities

## Public API:
- ObjectDocumentModel(paragraphs): Creates document model from iterable of paragraphs
- Paragraph(sentences): Creates paragraph from iterable of sentences  
- Sentence(text, tokenizer, is_heading=False): Creates sentence with tokenization support

## Dependencies:
- Internal: None
- External: Uses `itertools.chain` for flattening collections

## Constraints:
- All paragraph objects must have `sentences`, `headings`, and `words` attributes
- All sentence objects must be instances of Sentence class
- Document and paragraph structural data are immutable after creation

---

## Files

- [`_document.py`](dom/_document.md)
- [`_paragraph.py`](dom/_paragraph.md)
- [`_sentence.py`](dom/_sentence.md)

