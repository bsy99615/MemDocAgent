# `sumy.models`

## Tree:
models/
├── dom/
│   ├── _document.py
│   ├── _paragraph.py
│   └── _sentence.py
└── tf.py

## Role:
Provides foundational data structures for representing and analyzing document content, including both hierarchical document models and term frequency computations.

## Description:
The models module serves as the core data abstraction layer for the sumy library, offering two primary categories of components:

1. **Document Object Model (DOM)**: Hierarchical structures for organizing text content into sentences, paragraphs, and full documents, enabling structured document processing and traversal.

2. **Term Frequency Models**: Abstractions for computing and manipulating term frequency statistics, supporting TF-IDF calculations and vector-based text analysis.

These components work together to provide a robust foundation for text summarization algorithms, ensuring consistent data representation and efficient processing of document content.

## Components:
- ObjectDocumentModel: Main document container aggregating paragraphs
- Paragraph: Container for sentences within a document section
- Sentence: Atomic text unit with tokenization capabilities
- TfDocumentModel: Term frequency model for TF-based computations

## Public API:
- ObjectDocumentModel(paragraphs): Creates document model from iterable of paragraphs
- Paragraph(sentences): Creates paragraph from iterable of sentences  
- Sentence(text, tokenizer, is_heading=False): Creates sentence with tokenization support
- TfDocumentModel(words, tokenizer=None): Creates term frequency model from words or text

## Dependencies:
- Internal: None
- External: Uses `itertools.chain` for flattening collections

## Constraints:
- All paragraph objects must have `sentences`, `headings`, and `words` attributes
- All sentence objects must be instances of Sentence class
- Document and paragraph structural data are immutable after creation
- TfDocumentModel requires either words as sequence or string with tokenizer

---

## Files

- [`tf.py`](models/tf.md)

