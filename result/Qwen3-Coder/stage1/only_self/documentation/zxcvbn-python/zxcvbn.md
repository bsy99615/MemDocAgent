# `zxcvbn`

## Tree:
    zxcvbn/
    ├── __init__.py
    ├── __main__.py
    ├── feedback.py
    ├── matching.py
    ├── scoring.py
    └── time_estimates.py

## Role:
    Estimates password strength by implementing the zxcvbn algorithm for analyzing patterns and calculating guess probabilities.

## Description:
    The zxcvbn module provides a comprehensive password strength estimation system based on the zxcvbn algorithm developed by Dropbox. It analyzes passwords for common patterns, calculates the number of guesses required to crack them, estimates attack times for various scenarios, and provides security feedback to help users create stronger passwords.

    This module is used throughout the repository as the primary interface for password strength analysis. It's consumed by authentication systems, password validation services, and security auditing tools that need to assess password quality programmatically.

    The module follows a cohesive design principle where related functionality is grouped into logical components:
    - Pattern matching (matching.py) identifies structural elements in passwords
    - Scoring (scoring.py) calculates guess probabilities for identified patterns
    - Feedback generation (feedback.py) provides user-friendly security advice
    - Time estimation (time_estimates.py) converts guess counts into attack time estimates
    - Command-line interface (__main__.py) provides a terminal tool for password analysis

## Components:
    - zxcvbn.__init__.zxcvbn: Main entry point for password strength analysis
    - zxcvbn.__main__.cli: Command-line interface for password analysis
    - zxcvbn.__main__.JSONEncoder: Custom JSON encoder for serialization
    - zxcvbn.feedback.get_dictionary_match_feedback: Generates feedback for dictionary-based matches
    - zxcvbn.feedback.get_feedback: Provides overall feedback based on match analysis and score
    - zxcvbn.feedback.get_match_feedback: Generates feedback for specific pattern types
    - zxcvbn.matching.omnimatch: Applies all pattern matching strategies to a password
    - zxcvbn.scoring.most_guessable_match_sequence: Finds optimal pattern sequence using dynamic programming
    - zxcvbn.scoring.estimate_guesses: Estimates guess count for pattern matches
    - zxcvbn.time_estimates.estimate_attack_times: Calculates attack time estimates for different scenarios
    - zxcvbn.time_estimates.guesses_to_score: Maps guess counts to security strength scores

## Public API:
    - zxcvbn(password, user_inputs=None): Main function for password strength analysis
      - Analyzes password for patterns and calculates strength
      - Returns detailed analysis including guess count, attack times, and feedback
      - Accepts optional user inputs for enhanced pattern matching
    - zxcvbn.__main__.cli(): Command-line interface for password analysis
      - Parses command-line arguments
      - Reads password from stdin or prompts user
      - Outputs JSON-formatted analysis results
    - zxcvbn.__main__.JSONEncoder: Custom JSON encoder for serialization
      - Handles non-serializable objects by converting to strings
      - Used for JSON output in command-line interface

## Dependencies:
    - Internal imports:
        - zxcvbn.feedback: Provides feedback generation functions
        - zxcvbn.matching: Contains pattern matching algorithms
        - zxcvbn.scoring: Implements guess estimation calculations
        - zxcvbn.time_estimates: Handles time conversion and attack estimation
    - External imports:
        - json: Standard library for JSON serialization
        - re: Standard library for regular expression operations
        - decimal: Standard library for precise decimal arithmetic
        - collections: Standard library for data structures
        - itertools: Standard library for iterator operations
        - os: Standard library for OS-related operations (for stdin checking)
        - select: Standard library for I/O multiplexing (for non-blocking stdin)
        - getpass: Standard library for secure password input

## Constraints:
    - Callers must provide valid string passwords to the main zxcvbn function
    - User inputs should be iterable containing strings or convertible values
    - The module assumes all internal constants and dictionaries are properly initialized
    - Thread-safe: The module is stateless and can be safely used in concurrent environments
    - No initialization prerequisites required for basic usage
    - All functions expect consistent data structures as defined in their documentation

---

## Files

- [`__init__.py`](zxcvbn/__init__.md)
- [`__main__.py`](zxcvbn/__main__.md)
- [`feedback.py`](zxcvbn/feedback.md)
- [`matching.py`](zxcvbn/matching.md)
- [`scoring.py`](zxcvbn/scoring.md)
- [`time_estimates.py`](zxcvbn/time_estimates.md)

