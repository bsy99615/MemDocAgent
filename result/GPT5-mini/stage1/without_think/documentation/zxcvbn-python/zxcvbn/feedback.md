# `feedback.py`

## `zxcvbn.feedback.get_feedback` · *function*

## Summary:
Return user-facing, localized feedback for a password given its numeric strength score and the sequence of low-level matches; encourages adding words when the password is weak and suppresses feedback for sufficiently-strong scores.

## Description:
This function centralizes UI-facing feedback assembly for the top-level password-strength pipeline. Typical callers (no concrete call-sites provided in the supplied sources) are the public password-strength or assessment API routines that:
- compute a list of match objects for the candidate password (the matcher stage),
- compute a numeric score for the password (the scoring stage),
and then call this function to produce localized, short guidance shown to end users.

Why this logic is extracted:
- It separates the UI/message assembly from scoring and matching logic. It encapsulates decisions such as when to emit any feedback (score threshold), how to choose which match to explain (the longest match), and how to combine match-specific messages with higher-level suggestions (e.g., "Add another word or two").

## Args:
    score (int or numeric):
        - A numeric strength score where larger values indicate stronger passwords.
        - Behavior in this function: any score > 2 is treated as "strong enough" and causes the function to return an empty suggestions list with an empty warning (i.e., no actionable feedback).
        - No explicit range is enforced by this function; common callers typically use small integer scores (for example, 0..4) but only the relative comparison (> 2) is used here.

    sequence (list-like of dict):
        - A list (or list-like) of match objects produced by the matcher subsystem. Each match is expected to be a dict-like object with at least:
            * 'token' (str): the substring of the password matched. This function uses len(match['token']) to pick the longest match.
        - Matches should otherwise be compatible with get_match_feedback(match, is_sole_match) — i.e., they should contain the pattern-specific keys that get_match_feedback expects ('pattern' and branch-specific keys).
        - Interdependency: the function calls get_match_feedback(longest_match, is_sole_match) where is_sole_match is True exactly when len(sequence) == 1.

## Returns:
    dict
        - Always returns a dict with these keys:
            * 'warning' (str): a short localized message explaining a weakness; may be an empty string ''.
            * 'suggestions' (list[str]): zero or more short localized suggestion strings.
        - Possible return shapes and meanings:
            * If sequence is empty:
                - { 'warning': '', 'suggestions': [ "Use a few words, avoid common phrases.", "No need for symbols, digits, or uppercase letters." ] }
                - (These strings are produced via localization in the implementation; the English source strings are shown here.)
            * If score > 2:
                - { 'warning': '', 'suggestions': [] } — feedback is suppressed for sufficiently strong passwords.
            * Otherwise:
                - The function selects the match with the longest token and calls get_match_feedback(longest_match, is_sole_match).
                - If get_match_feedback returns a dict, this function prepends the extra suggestion "Add another word or two. Uncommon words are better." to feedback['suggestions'] and ensures feedback contains a 'warning' key (possibly set to '').
                - If get_match_feedback returns None (no match-specific advice), the function returns:
                    { 'warning': '', 'suggestions': [ "Add another word or two. Uncommon words are better." ] }
        - Note: All returned messages are localized strings (gettext) in the real implementation.

## Raises:
    - KeyError:
        * If a required key is missing from an element of sequence:
            - Access to sequence[0] and later sequence[1:] are safe because empty sequence is handled first; however, for non-empty sequence, missing 'token' in a match will raise KeyError when used to compute length.
        * Keys required by get_match_feedback for the chosen longest_match (for example, 'pattern' or other pattern-specific keys) may raise KeyError downstream; such exceptions propagate unchanged.
    - TypeError / AttributeError:
        * If sequence items are not dict-like or if match['token'] is not a string-like object, attempts to call len(match['token']) may raise TypeError/AttributeError.
    - Any exception raised by get_match_feedback will propagate up; this function does not catch exceptions from that call.

## Constraints:
    Preconditions:
        - Caller must pass sequence as an indexable, sized iterable (supports len() and indexing).
        - If sequence is non-empty, each element must contain a 'token' key whose value supports len().
        - Elements of sequence must meet get_match_feedback's expectations for match dictionary keys if match-specific feedback is desired.

    Postconditions:
        - The function returns a dict with keys 'warning' (str) and 'suggestions' (list[str]).
        - If get_match_feedback returned a dict, that returned dict will have been mutated in-place: the extra suggestion has been inserted at position 0 of feedback['suggestions'], and feedback['warning'] will be set to '' if it was falsy. If get_match_feedback returned None, a new dict is created and returned.
        - The original sequence list and the match objects inside it are not modified by this function.

## Side Effects:
    - Localization lookups: the function uses localized source strings (gettext) to build returned messages; this does not raise I/O or network activity but depends on the current locale/translation setup.
    - Mutation of returned feedback dict: when get_match_feedback returns a dict, this function mutates that dict in-place by inserting the "Add another word or two..." suggestion and possibly setting 'warning' to ''. This is a side effect on the object returned from get_match_feedback (not on the input sequence).
    - No file, network, stdout/stderr, database, or global-state writes are performed.

## Control Flow:
flowchart TD
    Start["Start"]
    CheckSeqEmpty{"len(sequence) == 0?"}
    Start --> CheckSeqEmpty
    CheckSeqEmpty -- Yes --> ReturnEmptySeq["Return {'warning':'', 'suggestions':[Use a few words..., No need for symbols...]}"]
    CheckSeqEmpty -- No --> CheckScore{"score > 2?"}
    CheckScore -- Yes --> ReturnSafe["Return {'warning':'', 'suggestions':[]}"]
    CheckScore -- No --> PickLongest["Select longest_match = longest token in sequence"]
    PickLongest --> CallMatchFB["feedback = get_match_feedback(longest_match, is_sole_match)"]
    CallMatchFB --> PrepareExtra["extra_feedback = 'Add another word or two. Uncommon words are better.'"]
    CallMatchFB --> FeedbackPresent{"feedback is truthy?"}
    FeedbackPresent -- True --> InsertExtra["Insert extra_feedback at start of feedback['suggestions']"]
    InsertExtra --> EnsureWarning["If not feedback['warning']: set feedback['warning']=''"]
    EnsureWarning --> ReturnFeedback["Return modified feedback dict"]
    FeedbackPresent -- False --> MakeNew["feedback = {'warning':'', 'suggestions':[extra_feedback]}"]
    MakeNew --> ReturnFeedback

## Examples:
- Empty sequence (user supplied a very short or empty password tokenization):
    Input:
        score = 0
        sequence = []
    Output:
        {
            'warning': '',
            'suggestions': [
                "Use a few words, avoid common phrases.",
                "No need for symbols, digits, or uppercase letters."
            ]
        }

- Score considered strong (no feedback emitted):
    Input:
        score = 3
        sequence = [ { 'token': 'correcthorsebatterystaple', 'pattern': 'dictionary', ... } ]
    Output:
        {
            'warning': '',
            'suggestions': []
        }

- Single longest match with match-specific feedback returned:
    Context:
        - Suppose the longest match is {'token': 'password', ...} and get_match_feedback(longest_match, is_sole_match=True)
          returns { 'warning': 'Common word', 'suggestions': ['Capitalize it, add digits'] }.
    Input:
        score = 1
        sequence = [ {'token': 'password', ...} ]
    Output (this function mutates the returned dict by prepending the extra suggestion):
        {
            'warning': 'Common word',
            'suggestions': [
                "Add another word or two. Uncommon words are better.",
                "Capitalize it, add digits"
            ]
        }

- No match-specific feedback (get_match_feedback returns None):
    Input:
        score = 1
        sequence = [ {'token': 'abc', ...}, {'token': '123', ...} ]  (none produce match feedback)
    Output:
        {
            'warning': '',
            'suggestions': [
                "Add another word or two. Uncommon words are better."
            ]
        }

## `zxcvbn.feedback.get_match_feedback` · *function*

## Summary:
Return human-readable feedback for a single password match: a localized warning and zero or more short suggestions describing why the matched token weakens the password and how to improve it.

## Description:
This function examines a single match object produced by the password-matching stage and maps that low-level match into user-facing feedback. It handles several match patterns (dictionary, spatial, repeat, sequence, regex, date) and either delegates to a specialized helper for dictionary matches or constructs a small dict containing a 'warning' string and a list of 'suggestions'.

Known callers within the codebase and typical context:
- No concrete call sites were provided with the supplied sources. Typically, a higher-level feedback aggregation routine iterates the list of matches produced by the matcher subsystem and calls this function for each match to build per-match feedback that is later aggregated and returned to the API consumer.

Reason for extraction:
- Converting match objects into user-friendly, localized messages is a distinct responsibility that is reused by the feedback assembly step. Extracting this logic keeps match-to-message mapping testable, localized, and separate from matching/scoring logic.

## Args:
    match (dict):
        - Required keys:
            * 'pattern' (str): The type of match. Expected values handled by this function are:
                - 'dictionary' — delegated to get_dictionary_match_feedback
                - 'spatial' — keyboard / keypad pattern
                - 'repeat' — repeated substrings
                - 'sequence' — character or numeric sequences
                - 'regex' — named regex matches (e.g., recent years)
                - 'date' — date-like matches
        - Pattern-specific keys accessed by branches:
            * If pattern == 'spatial': 'turns' (int) — number of direction changes in the keyboard pattern.
            * If pattern == 'repeat': 'base_token' (str) — the repeated unit; length is inspected.
            * If pattern == 'regex': 'regex_name' (str) — used to detect 'recent_year'.
            * If pattern == 'dictionary': this function delegates to get_dictionary_match_feedback(match, is_sole_match). See the get_dictionary_match_feedback component documentation for the dictionary branch's required keys, types, and semantics.
        - Notes:
            * Keys are accessed by direct indexing (match['...']) in many places; missing required keys will raise KeyError.
            * String types are expected where string operations or regexes would otherwise be used by delegated functions.

    is_sole_match (bool):
        - True if this match spans the entire password (no other matches). Some warnings are stronger or only emitted when this is True.

## Returns:
    - dict or None
    - When a branch produces feedback, the function returns a dict with these keys:
        * 'warning' (str): a short localized message explaining why the token is weak (may be empty string '').
        * 'suggestions' (list[str]): zero or more short localized suggestion strings advising how to improve the password.
    - Possible return shapes:
        * Delegation: for pattern == 'dictionary', this function returns whatever get_dictionary_match_feedback(match, is_sole_match) returns — see that component's documentation for exact shape and rules.
        * Direct returns (examples):
            - spatial -> {'warning': <str>, 'suggestions': [<str>]}
            - repeat -> {'warning': <str>, 'suggestions': [<str>]}
            - sequence -> {'warning': <str>, 'suggestions': [<str>]}
            - regex (regex_name == 'recent_year') -> {'warning': <str>, 'suggestions': [<str>, ...]}
            - date -> {'warning': <str>, 'suggestions': [<str>]}
        * None: If match['pattern'] has a value that is not handled (no matching branch) or the 'regex' branch does not match a recognized regex_name, the function falls through and returns None implicitly.

## Raises:
    - KeyError:
        * If 'pattern' is missing from match (first access is match['pattern']).
        * If a pattern-specific key accessed in a branch is missing:
            - 'turns' when pattern == 'spatial'
            - 'base_token' when pattern == 'repeat'
            - 'regex_name' when pattern == 'regex'
        * If pattern == 'dictionary', delegated function calls may raise KeyError for the keys that function expects — see get_dictionary_match_feedback documentation for details.
    - TypeError / AttributeError:
        * If values have unexpected types (e.g., 'base_token' is not a string and its length is queried, or 'turns' is not an int), Python may raise TypeError or AttributeError.
    - No other exceptions are raised by this function itself; localization lookup (gettext) is used to produce messages but does not change exception semantics.

## Constraints:
    Preconditions:
        - Caller must supply a dict-like match containing at minimum the key 'pattern' with a string value.
        - If pattern-specific branches will be used by the caller, the corresponding keys described above must be present and of the expected type.
        - is_sole_match should be a boolean.

    Postconditions:
        - If a dict is returned, it always contains the keys 'warning' (str) and 'suggestions' (list[str]).
        - The function does not mutate the provided match object.
        - If the pattern is unrecognized or no specialized feedback is defined for a recognized pattern/regex_name, the function returns None.

## Side Effects:
    - None intrinsic to this function: no I/O, no network calls, no global state mutation, no writes to external systems.
    - The returned messages are localized strings produced via gettext; the function assumes a translation helper (commonly exposed as _) is available in the module scope.
    - Delegation to get_dictionary_match_feedback may execute that function's internal logic but does not imply side effects beyond its documented behavior.

## Control Flow:
flowchart TD
    Start["Start"]
    ReadPattern["Read match['pattern']"]
    Start --> ReadPattern
    ReadPattern --> IsDictionary{"pattern == 'dictionary'?"}
    IsDictionary -- Yes --> Delegate["Return get_dictionary_match_feedback(match, is_sole_match)"]
    IsDictionary -- No --> IsSpatial{"pattern == 'spatial'?"}
    IsSpatial -- Yes --> SpatialTurns{"Check match['turns'] == 1"}
    SpatialTurns -- True --> WarnSpatialStraight["warning = 'Straight rows...'"]
    SpatialTurns -- False --> WarnSpatialShort["warning = 'Short keyboard patterns...'"]
    WarnSpatialStraight --> ReturnSpatial["return {'warning':..., 'suggestions':[...]}"]
    WarnSpatialShort --> ReturnSpatial
    IsSpatial -- No --> IsRepeat{"pattern == 'repeat'?"}
    IsRepeat -- Yes --> BaseLenCheck{"len(match['base_token']) == 1?"}
    BaseLenCheck -- True --> WarnRepeatShort["warning = 'Repeats like \"aaa\"...'"]
    BaseLenCheck -- False --> WarnRepeatLong["warning = 'Repeats like \"abcabcabc\"...'"]
    WarnRepeatShort --> ReturnRepeat["return {'warning':..., 'suggestions':[...]}"]
    WarnRepeatLong --> ReturnRepeat
    IsRepeat -- No --> IsSequence{"pattern == 'sequence'?"}
    IsSequence -- Yes --> ReturnSequence["return {'warning': 'Sequences like ...', 'suggestions':[...]}"]
    IsSequence -- No --> IsRegex{"pattern == 'regex'?"}
    IsRegex -- Yes --> IsRecentYear{"match['regex_name'] == 'recent_year'?"}
    IsRecentYear -- True --> ReturnRecentYear["return {'warning': 'Recent years...', 'suggestions':[...]}"]
    IsRecentYear -- False --> Fallthrough["No feedback for other regex_name -> implicit None"]
    IsRegex -- No --> IsDate{"pattern == 'date'?"}
    IsDate -- Yes --> ReturnDate["return {'warning': 'Dates are often easy to guess.', 'suggestions':[...]}"]
    IsDate -- No --> Fallthrough
    Fallthrough --> End["Return None (no feedback)"]

## Examples:
- Spatial pattern (straight row):
    Input: match = {'pattern': 'spatial', 'turns': 1}, is_sole_match = False
    Output: {'warning': 'Straight rows of keys are easy to guess.', 'suggestions': ['Use a longer keyboard pattern with more turns.']}

- Repeat pattern (single-character repeat):
    Input: match = {'pattern': 'repeat', 'base_token': 'a'}, is_sole_match = True
    Output: {'warning': 'Repeats like "aaa" are easy to guess.', 'suggestions': ['Avoid repeated words and characters.']}

- Regex recent year:
    Input: match = {'pattern': 'regex', 'regex_name': 'recent_year'}, is_sole_match = True
    Output: {'warning': 'Recent years are easy to guess.', 'suggestions': ['Avoid recent years.', 'Avoid years that are associated with you.']}

- Date match:
    Input: match = {'pattern': 'date'}, is_sole_match = False
    Output: {'warning': 'Dates are often easy to guess.', 'suggestions': ['Avoid dates and years that are associated with you.']}

- Dictionary match delegation:
    Input: match = {'pattern': 'dictionary', ...}, is_sole_match = True
    Behavior: Delegates to get_dictionary_match_feedback(match, is_sole_match) and returns that function's result. See the get_dictionary_match_feedback documentation for the dictionary branch's expected keys and return conventions.

Notes:
- All messages in returned dicts are produced via localization (gettext) in the original implementation; the English strings shown above are source text and may vary under localization.
- If you need to handle an additional pattern, add a branch that returns the same shape: {'warning': <str>, 'suggestions': [<str>, ...]}.

## `zxcvbn.feedback.get_dictionary_match_feedback` · *function*

## Summary:
Return human-readable feedback for a single dictionary match: a concise warning string (if any) plus zero or more suggestion strings that describe why the match is weak and how to improve the password.

## Description:
This function consumes a single dictionary match (the data structure produced by the password-matching stage of a password-strength estimator) and determines:
- a warning message when the match indicates a commonly-guessable token (for example, a frequent password, an English word, or a name), and
- a short list of suggestions related to capitalization, predictable substitutions, reversing, and similar patterns.

Known callers within the provided context:
- No concrete call sites were included with the provided source. Typically this function is invoked by higher-level feedback assembly code after the password has been segmented into matches: for each match produced by the matcher subsystem, this function is called to produce per-match feedback which is later aggregated and returned to the caller.

Reason for extraction:
- The logic converts a low-level match object into user-facing feedback. It is separated so match-to-feedback mapping is reusable, testable, and kept independent of overall match-aggregation or scoring code.

## Args:
    match (dict): A mapping describing a dictionary match. Expected keys and types:
        - 'dictionary_name' (str): Identifier for the dictionary that matched, e.g. 'passwords', 'english', 'surnames', 'male_names', 'female_names', or other dictionary identifiers.
        - 'token' (str): The substring of the password that matched the dictionary entry.
        - 'reversed' (bool): True if the match was found by reversing the token before matching.
        - 'rank' (int): (Used only when 'dictionary_name' == 'passwords') The 1-based frequency rank of the matched password in the passwords dictionary (lower is more common).
        - 'guesses_log10' (float or int): (Used only when 'dictionary_name' == 'passwords') log10 of the estimated number of guesses for this match.
        - 'l33t' (bool, optional): True if the match involved l33t (leet) substitutions; may be absent (treated as False).
      Notes:
        - The function reads keys with either direct indexing or .get; missing required keys will raise KeyError where direct indexing is used.
        - 'token' must be a string because the function runs regex searches against it.
    is_sole_match (bool): True if this match covers the entire password (no other matches). When True, some warnings are stronger (e.g., "A word by itself is easy to guess.").

## Returns:
    dict: A dictionary with the following keys:
        - 'warning' (str): A single short warning message describing why the matched token weakens the password, or an empty string if no warning applies.
        - 'suggestions' (list[str]): A list (possibly empty) of short suggestion strings suggesting how the password could be made harder to guess (e.g., comments on capitalization, reversing, or l33t substitution).
    Possible return shapes:
        - {'warning': '', 'suggestions': []} — no concerns found for the provided match.
        - {'warning': '<non-empty message>', 'suggestions': [ ... ]} — when warnings and/or suggestions apply.

## Raises:
    KeyError:
        - If required keys are missing from match:
            * 'dictionary_name' is accessed directly; its absence raises KeyError.
            * 'token' is accessed directly; its absence raises KeyError.
            * 'reversed' is accessed directly; its absence raises KeyError.
        - 'rank' and 'guesses_log10' are only accessed when 'dictionary_name' == 'passwords'; if those keys are missing in that branch, a KeyError will be raised.
    TypeError / AttributeError:
        - If 'token' is not a string (so regex search calls fail), a TypeError or AttributeError may be raised by the regex search operations.

## Constraints:
Preconditions:
    - Caller must provide a dict-like match with at least the keys 'dictionary_name', 'token', and 'reversed' present with appropriate types.
    - If 'dictionary_name' == 'passwords' and the code path relies on rank or guesses_log10, those keys must be present and numeric.
    - is_sole_match must be a boolean value indicating whether this match covers the whole password.

Postconditions:
    - The returned dict always contains the keys 'warning' (string) and 'suggestions' (list of strings).
    - The function performs no mutations of the provided match object.

## Side Effects:
    - None. The function does not perform I/O, network calls, mutate global state, or alter the provided match mapping.

## Control Flow:
flowchart TD
    Start["Start"]
    ReadDict["Read match['dictionary_name']"]
    Start --> ReadDict
    ReadDict --> IsPasswords{"dictionary_name == 'passwords'?"}
    IsPasswords -- Yes --> PasswordsBranch["If is_sole_match and not l33t and not reversed:"]
    PasswordsBranch --> RankCheck{"rank <= 10 ? <=100 ?"}
    RankCheck --> Top10["warning = top-10"]
    RankCheck --> Top100["warning = top-100"]
    RankCheck --> VeryCommon["warning = very common"]
    PasswordsBranch --> ElseGuesses{"elif guesses_log10 <= 4"}
    ElseGuesses --> SimilarPassword["warning = similar to commonly used"]
    IsPasswords -- No --> IsEnglish{"dictionary_name == 'english'?"}
    IsEnglish -- Yes --> EnglishBranch{"if is_sole_match -> warning 'word by itself' else ''"}
    IsEnglish -- No --> IsName{"dictionary in [surnames,male_names,female_names]?"}
    IsName -- Yes --> NameBranch{"if is_sole_match -> warning 'names by themselves' else 'common names' warning"}
    IsName -- No --> DefaultWarning["warning = ''"]
    AfterWarning["Compute suggestions:"]
    DefaultWarning --> AfterWarning
    SimilarPassword --> AfterWarning
    Top10 --> AfterWarning
    Top100 --> AfterWarning
    VeryCommon --> AfterWarning
    EnglishBranch --> AfterWarning
    NameBranch --> AfterWarning
    AfterWarning --> CheckStartUpper{"START_UPPER.search(token)?"}
    CheckStartUpper -- Yes --> AddCapitalizationSuggestion["add 'Capitalization doesn't help very much.'"]
    CheckStartUpper -- No --> CheckAllUpper{"ALL_UPPER.search(token) and token.lower() != token?"}
    CheckAllUpper -- Yes --> AddAllUpperSuggestion["add 'All-uppercase is almost as easy...'"]
    CheckAllUpper -- No --> ContinueSuggestions["no capitalization suggestion"]
    ContinueSuggestions --> ReversedCheck{"if reversed and len(token) >= 4"}
    ReversedCheck -- Yes --> AddReversedSuggestion["add 'Reversed words aren't much harder...'"]
    ContinueSuggestions --> L33tCheck{"if l33t == True"}
    L33tCheck -- Yes --> AddL33tSuggestion["add 'Predictable substitutions ...'"]
    L33tCheck -- No --> End
    AddL33tSuggestion --> End
    AddReversedSuggestion --> L33tCheck
    AddAllUpperSuggestion --> ReversedCheck
    AddCapitalizationSuggestion --> ReversedCheck
    End["Return {'warning': warning, 'suggestions': suggestions}"]

## Examples (plain-language):
- Example 1 — common password:
  If match describes a token found in the 'passwords' dictionary with rank 8, is_sole_match True, not reversed and not l33t, the function will return a non-empty warning indicating a top-10 common password and may include no suggestions (unless capitalization or other features triggered suggestions).

- Example 2 — single English word:
  If match has dictionary_name 'english', token 'sunshine', and is_sole_match True, the function will return a warning that "A word by itself is easy to guess." and may add suggestions about capitalization if the token's case pattern triggers them.

- Example 3 — reversed short word:
  If match shows reversed=True and the token length is less than 4, the reversed-word suggestion is not produced (suggestions about reversed words require length >= 4).

- Example 4 — l33t substitutions:
  If match.get('l33t') is True, the suggestions list will include advice that predictable substitutions (e.g., '@' for 'a') do not help much.

Notes:
- All returned messages are intended for end-user display and are localized via gettext in the original implementation; the content of messages is language-dependent when localization is enabled.

