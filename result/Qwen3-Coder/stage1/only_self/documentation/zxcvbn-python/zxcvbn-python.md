# `zxcvbn-python`

## Tree:
zxcvbn-python/
└── zxcvbn/
    ├── __init__.py
    ├── __main__.py
    ├── feedback.py
    ├── matching.py
    ├── scoring.py
    └── time_estimates.py

## Purpose:
This repository implements the zxcvbn password strength estimation algorithm originally developed by Dropbox. It addresses the critical need for robust password security assessment in applications that require strong authentication mechanisms. Unlike simple length or character-type checks, zxcvbn analyzes passwords for common patterns, sequences, and predictable substitutions to provide meaningful security assessments.

Target users include security engineers, application developers building authentication systems, and organizations requiring password policy enforcement. The tool is particularly valuable in scenarios involving user registration forms, password reset workflows, security auditing processes, and compliance requirements where automated password strength evaluation is essential.

The repository positions itself as a standalone library that can be integrated into larger applications or used as a command-line tool for quick password analysis.

## Architecture:
```mermaid
flowchart TD
    A[Password Input] --> B[zxcvbn()]
    B --> C[Pattern Matching]
    C --> D[Guess Estimation]
    D --> E[Attack Time Estimation]
    E --> F[Feedback Generation]
    F --> G[Result Output]
    B --> H[User Inputs Processing]
    H --> C
```

The system follows a pipeline architecture where password analysis flows through several distinct processing stages:
1. Pattern matching identifies structural elements in passwords (dictionary words, sequences, repeated characters)
2. Guess estimation calculates the computational effort required to crack patterns using sophisticated algorithms
3. Attack time estimation converts guess counts into real-world timeframes for offline and online attacks
4. Feedback generation provides user-friendly security guidance tailored to the specific weaknesses detected

Key architectural patterns include:
- Modular decomposition: Each core functionality is separated into dedicated modules
- Functional approach: Stateless processing functions that transform input to output
- Data-driven design: All processing relies on consistent data structures and patterns

## Entry Points:
- **Importable API**: `from zxcvbn import zxcvbn`
  - Primary function for password strength analysis
  - Accepts password string and optional user inputs (names, birthdates, etc.)
  - Returns comprehensive analysis including guess count, attack times, and actionable feedback
  - Ideal for integration into web applications, authentication systems, and security tools
  
- **Command-Line Interface**: `python -m zxcvbn [password]`
  - Terminal-based password analysis for quick assessments
  - Reads password from command line argument or interactive prompt
  - Outputs JSON-formatted results for programmatic consumption
  - Useful for security testing, batch processing, and manual analysis

## Core Features:
- Password strength estimation based on pattern recognition
  - Implemented in: zxcvbn.scoring, zxcvbn.matching
  - Analyzes dictionary matches, sequences, repeated characters, and keyboard patterns
- Guess count calculation for various attack scenarios  
  - Implemented in: zxcvbn.scoring, zxcvbn.time_estimates
  - Estimates computational effort for offline brute-force and online rate-limited attacks
- Real-world attack time estimation (offline, online attacks)
  - Implemented in: zxcvbn.time_estimates
  - Converts guess counts into years, days, or seconds based on attack speed assumptions
- User-friendly security feedback and suggestions
  - Implemented in: zxcvbn.feedback
  - Provides actionable advice to help users create stronger passwords
- Support for custom user inputs to improve pattern matching
  - Implemented in: zxcvbn.matching, zxcvbn.scoring
  - Allows inclusion of personal information to detect personalized weak passwords

## Dependencies:
- **Standard Library**: 
  - json, re, decimal, collections, itertools, os, select, getpass
  - Used for core functionality like serialization, regex operations, precision arithmetic, and OS interactions

## Configuration:
No configuration files or environment variables are required. The system operates with default parameters that provide robust password analysis out-of-the-box. Advanced users can customize behavior by passing appropriate arguments to the main zxcvbn() function.

## Extension Points:
The system supports extension through:
- Custom user inputs: Pass additional personal information to improve pattern matching accuracy
- Plugin-like architecture: Individual modules can be replaced or extended independently
- Direct API integration: Developers can build upon the core analysis functions for specialized use cases

---

## Modules

- [`zxcvbn`](zxcvbn.md)

