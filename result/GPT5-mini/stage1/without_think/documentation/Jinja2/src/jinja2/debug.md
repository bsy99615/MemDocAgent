# `debug.py`

## `src.jinja2.debug.rewrite_traceback_stack` · *function*

## Summary:
Transforms the active exception's Python traceback into a Jinja-aware traceback chain and returns the same exception with the reconstructed traceback attached.

## Description:
This function inspects the current exception via sys.exc_info(), casts the exception and traceback values, and then reconstructs a traceback chain that filters internal frames and replaces template frames with synthetic traceback frames produced by fake_traceback. The reconstructed chain is attached to the original exception and returned.

Known callers within the provided snapshot:
- No callers were present in the provided memory snapshot. In typical use this function is called inside an except: handler in the Jinja runtime, template rendering, or template compilation pipeline immediately after an exception is caught to convert low-level Python tracebacks into template-level tracebacks before re-raising or reporting.

Why this logic is extracted:
- Encapsulates the non-trivial mapping from Python tracebacks to template-aware tracebacks:
    * isolates filtering of internal runtime frames (internal_code),
    * isolates the creation of synthetic traceback nodes for template frames (fake_traceback),
    * centralizes the logic that mutates the exception (translated/source flags) for TemplateSyntaxError,
    * makes the conversion reusable across multiple exception handlers.

## Args:
    source (t.Optional[str]):
        Optional template source text to attach when the active exception is a TemplateSyntaxError that has not yet been translated. Default: None.
        - When the active exception is a TemplateSyntaxError and exc_value.translated is False, the function sets exc_value.translated = True and exc_value.source = source.

## Returns:
    BaseException:
        The same exception object that was active when the function was called, returned from exc_value.with_traceback(tb_root).
        - The returned exception has a traceback chain constructed as follows:
            * If the active exception is a TemplateSyntaxError and not yet translated: a top fake traceback is created using fake_traceback(exc_value, None, exc_value.filename or "<unknown>", exc_value.lineno) and becomes the head of processing.
            * Otherwise: the current traceback is advanced once (tb = tb.tb_next) to skip the current frame before processing.
            * The function iterates remaining tb frames, skipping frames whose tb.tb_frame.f_code is in internal_code, and for frames whose tb.tb_frame.f_globals contains "__jinja_template__" it replaces the frame with fake_traceback(exc_value, tb, template.filename, lineno) where lineno = template.get_corresponding_lineno(tb.tb_lineno). Non-template frames are preserved.
            * The collected frames (or synthetic frames) are reversed and linked by setting tb.tb_next pointers so the resulting chain is in original order.
        - If no frames survive processing, the returned exception may have a None traceback (exc_value.with_traceback(None)).

## Raises:
    AttributeError:
        If called when there is no active traceback (sys.exc_info()[2] is None) and the active exception is not a TemplateSyntaxError, the code executes tb = tb.tb_next and will raise AttributeError because tb is None. In normal use this function must be invoked from within an except: block where a traceback is present.
    Propagated exceptions:
        - Any exception raised by fake_traceback, template.get_corresponding_lineno, or attribute accesses on the active exception (for example, if exc_value lacks expected attributes translated/filename/lineno) will propagate.

## Constraints:
Preconditions:
    - Must be called while an exception is being handled (inside an except handler) so sys.exc_info() returns a (type, value, traceback) triple where traceback is not None, except in the TemplateSyntaxError branch which synthesizes its own fake traceback.
    - The module-level names used by the function must be present and have the expected behavior:
        * internal_code: a collection (e.g., set) of CodeType objects used to identify and skip internal runtime frames.
        * fake_traceback: callable that returns a TracebackType-like object for a given exception, original traceback frame (or None), filename, and lineno.
        * Template objects referenced via frame f_globals["__jinja_template__"] must implement filename (str) and get_corresponding_lineno(py_lineno: int) -> int.

Postconditions:
    - If exc_value is a TemplateSyntaxError and exc_value.translated was False, then after the call:
        * exc_value.translated is True
        * exc_value.source is set to the provided source value
    - The returned exception has a traceback chain whose tb_next pointers have been set to the reconstructed sequence built by this function.

## Side Effects:
    - Mutates the active exception in the TemplateSyntaxError case:
        * sets exc_value.translated = True
        * sets exc_value.source = source
        * calls exc_value.with_traceback(None) (to detach the original traceback; the return value is not captured)
    - Builds and mutates TracebackType objects by assigning tb.tb_next to re-link frames.
    - Reads frame globals (tb.tb_frame.f_globals) and inspects frame code objects (tb.tb_frame.f_code).
    - Calls external helpers and template mapping functions (fake_traceback and template.get_corresponding_lineno).
    - No file or network I/O is performed by this function itself.

## Control Flow:
flowchart TD
    A[Start: called inside except] --> B{exc_value is TemplateSyntaxError and exc_value.translated is False?}
    B -- Yes --> C[set exc_value.translated=True; exc_value.source=source; exc_value.with_traceback(None)]
    C --> D[tb = fake_traceback(exc_value, None, exc_value.filename or "<unknown>", exc_value.lineno)]
    B -- No --> E[tb = tb.tb_next (advance past current frame)]
    D --> F[while tb is not None:]
    E --> F
    F --> G{tb is None?}
    G -- No --> H{tb.tb_frame.f_code in internal_code?}
    H -- Yes --> I[tb = tb.tb_next; continue]
    H -- No --> J{__jinja_template__ in tb.tb_frame.f_globals?}
    J -- Yes --> K[lineno = template.get_corresponding_lineno(tb.tb_lineno); fake_tb = fake_traceback(...); append fake_tb to stack]
    J -- No --> L[append original tb to stack]
    K --> M[tb = tb.tb_next]
    L --> M
    I --> M
    M --> F
    G -- Yes --> N[reverse collected stack; set tb.tb_next pointers to relink]
    N --> O[return exc_value.with_traceback(new_head)]

## Helper contracts (expected; not defined here):
- fake_traceback(exc_value: BaseException, orig_tb: typing.Optional[TracebackType], filename: str, lineno: int) -> TracebackType
    - Produces a TracebackType-like node whose frame reports filename and lineno for error reporting. orig_tb may be None for a top synthetic frame.
- Template object stored under "__jinja_template__" in frame f_globals:
    - Attributes/methods used:
        * filename: str
        * get_corresponding_lineno(py_tb_lineno: int) -> int

## Examples:
Typical usage in an except block to convert and re-raise the same exception:

    try:
        result = template.render(ctx)
    except Exception:
        exc = rewrite_traceback_stack(source=optional_source_text)
        # exc is the same exception with a Jinja-aware traceback attached
        raise exc

TemplateSyntaxError-specific example (during parsing/compilation):

    try:
        compile_template(source_text)
    except TemplateSyntaxError:
        exc = rewrite_traceback_stack(source=source_text)
        raise exc

Notes:
- The function uses t.cast internally to coerce the values returned by sys.exc_info() to BaseException and TracebackType; the implementation assumes the presence of a traceback in normal use (see Raises).
- Because the function mutates tb.tb_next pointers, the fake_traceback implementation must return TracebackType objects that are safe to link by assignment to tb_next.

## `src.jinja2.debug.fake_traceback` · *function*

*No documentation generated.*

## `src.jinja2.debug.get_template_locals` · *function*

*No documentation generated.*

