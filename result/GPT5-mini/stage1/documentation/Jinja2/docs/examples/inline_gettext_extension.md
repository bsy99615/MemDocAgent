# `inline_gettext_extension.py`

## `docs.examples.inline_gettext_extension.InlineGettext` · *class*

*No documentation generated.*

### `docs.examples.inline_gettext_extension.InlineGettext.filter_stream` · *method*

## Summary:
Transforms an incoming Jinja2 token stream by detecting inline gettext-style expressions and replacing them with explicit trans / endtrans block tokens; does not modify the InlineGettext instance state.

## Description:
This generator inspects successive tokens produced by the Jinja2 lexer and rewrites portions of "data" tokens that match inline gettext patterns into a sequence of Jinja2 block tokens that emulate a {% trans %}...{% endtrans %} block. It:
- passes through non-"data" tokens unchanged,
- splits "data" tokens into segments and yields them as separate Token objects,
- when an inline gettext opening is found, yields block_begin, name("trans"), block_end tokens,
- tracks nested parentheses inside the gettext expression using paren_stack,
- when the matching closing boundary is found and all parentheses are balanced, yields block_begin, name("endtrans"), block_end tokens.

Known callers / invocation context:
- This method is an override of the Jinja2 Extension.filter_stream hook and is invoked by the Jinja2 template compilation pipeline. It runs after the lexer produces the initial token stream and before parsing, allowing the extension to rewrite tokens into blocks the parser will understand.
- Typical lifecycle stage: template compilation/token-stream transformation step performed by the Jinja2 runtime when loading or compiling a template.

Why this is a separate method:
- The logic performs a streaming token transformation (scan/split/yield) which is orthogonal to parsing or rendering; isolating it as filter_stream allows the extension to operate on tokens incrementally without changing the parser or lexer internals and keeps the regex and token-handling logic centralized and testable.

## Args:
    self (InlineGettext): Extension instance (not read or modified by this method).
    stream (iterable[jinja2.lexer.Token]): An iterable/generator of Token objects produced by the Jinja2 lexer. Each Token must have the attributes:
        - type (str): token kind (e.g., "data", "name", etc.)
        - value (str): token text for "data" tokens
        - lineno (int): line number where the token starts
      The stream object itself is expected to expose .name and .filename attributes (used when raising TemplateSyntaxError).

## Returns:
    generator[jinja2.lexer.Token]:
        Yields jinja2.lexer.Token instances. Possible yielded token types and meanings:
        - "data": plain template text segments (including escaped characters handled by this method)
        - "block_begin": beginning of a synthetic block token (value None)
        - "name": block name tokens with values "trans" or "endtrans"
        - "block_end": end of a synthetic block token (value None)
      Edge cases:
        - The generator yields multiple Token items per input token (splitting "data" tokens into pieces).
        - When an escape sequence is matched (a backslash immediately preceding a match token), the backslash is removed and the unescaped character is yielded inside a "data" token.

## Raises:
    jinja2.exceptions.TemplateSyntaxError:
        Raised if the token stream ends while an opened gettext expression has not been closed (paren_stack != 0). The exception message is exactly "unclosed gettext expression". It is raised with the following positional information:
            - lineno: token.lineno of the last token processed
            - name: stream.name
            - filename: stream.filename

## State Changes:
    Attributes READ:
        - None of self's attributes are read by this method.
        - Module-level regexes _outside_re and _inside_re are read to find matches.
    Attributes WRITTEN:
        - None of self's attributes are modified.

## Constraints:
    Preconditions:
        - stream must be an iterable/generator of Token objects whose Token attributes (type, value, lineno) follow jinja2.lexer.Token conventions.
        - stream must have .name and .filename attributes (used for error reporting).
        - Module-level regexes _outside_re and _inside_re must be compiled and behave as expected: _outside_re matches the start/escape/boundary of an inline gettext expression when not currently inside one, and _inside_re matches internal tokens or parentheses while inside an expression.
    Postconditions:
        - For each input token, either the original token is yielded (if token.type != "data") or a sequence of tokens is yielded that together represent the original text with inline gettext expressions replaced by an explicit trans/endtrans block token sequence.
        - The method does not leave any lasting change on the InlineGettext instance (self).
        - If the stream completes without mismatched parentheses, no exception is raised and all paren_stack balancing will be resolved to zero.

## Side Effects:
    - Consumes the provided stream iterator/generator; tokens yielded by the stream are processed in order and not re-emitted unchanged unless appropriate.
    - Emits new Token objects; it does not mutate tokens in-place.
    - No I/O is performed and no external services are contacted.
    - If the stream ends with an open gettext expression, a TemplateSyntaxError is raised referencing stream.name and stream.filename.

