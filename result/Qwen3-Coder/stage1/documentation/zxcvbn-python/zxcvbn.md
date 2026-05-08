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
    Provides comprehensive password strength estimation by analyzing patterns, calculating guess counts, and generating user feedback

## Description:
The zxcvbn module implements Dropbox's zxcvbn password strength estimation algorithm. It analyzes passwords for predictable patterns, calculates the computational effort required to guess them, and provides actionable feedback for improving password security. This module serves as a complete password strength analyzer that goes beyond simple complexity checks to understand real-world password cracking patterns.

The module is organized into distinct layers:
- Pattern matching: Identifies dictionary words, spatial patterns, repeated sequences, and other predictable structures
- Scoring: Computes the number of guesses required for each pattern type
- Feedback generation: Creates human-readable suggestions for improving password strength
- Time estimation: Converts guess counts into meaningful time estimates for different attack scenarios

## Components:
    - zxcvbn.__init__.zxcvbn: Main entry point for password strength analysis
    - zxcvbn.__main__.cli: Command-line interface for interactive password analysis
    - zxcvbn.feedback: Generates user-facing feedback and suggestions
    - zxcvbn.matching: Detects various password patterns and structures
    - zxcvbn.scoring: Calculates guess counts for different pattern types
    - zxcvbn.time_estimates: Converts guess counts to time estimates for attack scenarios

## Public API:
    - zxcvbn(password, user_inputs=None): Main function to analyze password strength
    - zxcvbn.__main__.cli(): Command-line interface for password analysis
    - zxcvbn.feedback.get_feedback(score, sequence): Generate feedback for password analysis
    - zxcvbn.matching.omnimatch(password): Find all pattern matches in a password
    - zxcvbn.scoring.estimate_guesses(match, password): Estimate guesses for a pattern match
    - zxcvbn.time_estimates.estimate_attack_times(guesses): Convert guess counts to time estimates

## Dependencies:
    - Internal: 
        - zxcvbn.feedback: For generating user feedback
        - zxcvbn.matching: For pattern detection
        - zxcvbn.scoring: For guess count calculations
        - zxcvbn.time_estimates: For time estimation conversions
    - External: 
        - re: Regular expression support for pattern matching
        - math: Mathematical functions for logarithms and calculations
        - json: JSON serialization for CLI output
        - getpass: Secure password input for CLI
        - select: Input detection for CLI

## Constraints:
    - All functions expect valid string inputs for passwords
    - Pattern matching functions require properly formatted match dictionaries
    - Time estimation functions assume standard attack parameters
    - Thread-safe: Functions are stateless and can be called concurrently
    - Initialization: No special setup required - all functions are self-contained

---

## Files

- [`__init__.py`](zxcvbn/__init__.md)
- [`__main__.py`](zxcvbn/__main__.md)
- [`feedback.py`](zxcvbn/feedback.md)
- [`matching.py`](zxcvbn/matching.md)
- [`scoring.py`](zxcvbn/scoring.md)
- [`time_estimates.py`](zxcvbn/time_estimates.md)

