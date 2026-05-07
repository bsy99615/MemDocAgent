# `zxcvbn-python`

## Tree:
zxcvbn/
├── __init__.py
├── __main__.py
├── feedback.py
├── matching.py
├── scoring.py
└── time_estimates.py

## Purpose:
The zxcvbn-python library provides a sophisticated password strength estimation system that analyzes real-world password patterns and guessability rather than relying solely on simple complexity checks. It identifies common mistakes such as dictionary words, sequences, and predictable substitutions to deliver accurate strength assessments and actionable feedback.

Target users include web developers building authentication systems, security professionals evaluating password policies, and application developers seeking robust password validation tools. The system is particularly valuable in environments where traditional password complexity rules fail to capture actual security risks.

In the broader ecosystem, zxcvbn serves as a standalone password strength analyzer that can be integrated into web applications, command-line tools, or security frameworks. It's designed to replace simplistic character-counting approaches with intelligent pattern recognition and guess estimation.

## Architecture:
```mermaid
flowchart TD
    A[zxcvbn(password, user_inputs)] --> B[Pattern Matching]
    B --> C[Guess Estimation]
    C --> D[Time Estimation]
    D --> E[Feedback Generation]
    E --> F[Result]
    
    B --> G[matching.omnimatch]
    G --> H[scoring.most_guessable_match_sequence]
    H --> I[scoring.estimate_guesses]
    I --> J[time_estimates.estimate_attack_times]
    J --> K[feedback.get_feedback]
    K --> L[time_estimates.display_time]
```

The system follows a pipeline architecture where each stage builds upon the previous one:
1. **Pattern Matching**: Identifies various password weaknesses using multiple strategies
2. **Guess Estimation**: Computes how many guesses would be required to crack the password
3. **Time Estimation**: Converts guess counts into meaningful time estimates for different attack scenarios
4. **Feedback Generation**: Provides actionable advice based on the analysis

## Entry Points:
- **zxcvbn(password, user_inputs=None)**: Primary function for password strength analysis
  - Accepts password string and optional user input list
  - Returns comprehensive analysis including strength score, time estimates, and feedback
  - Intended for programmatic integration in applications

- **Command-Line Interface**: Available via `python -m zxcvbn`
  - Accepts password as argument or reads from stdin
  - Outputs JSON-formatted results for automation and testing
  - Designed for quick analysis and integration into shell scripts

## Core Features:
- **Pattern Recognition**: Identifies dictionary words, sequences, spatial patterns, repeated characters, and more
- **Intelligent Guess Estimation**: Uses sophisticated algorithms to compute realistic guess counts
- **Attack Time Calculation**: Estimates cracking times for various attack scenarios (online/offline, slow/fast hashing)
- **Actionable Feedback**: Provides specific suggestions to improve password strength
- **User Input Awareness**: Incorporates personal information to avoid false positives

## Dependencies:
- **Internal Dependencies**:
  - `matching`: Pattern identification and classification
  - `scoring`: Guess count computation and entropy analysis
  - `time_estimates`: Conversion of guesses to time estimates
  - `feedback`: Human-readable guidance generation

- **External Dependencies**:
  - `datetime`: Timing measurements for performance analysis
  - `decimal`: Precise numerical calculations for large numbers
  - `json`: Serialization of results for CLI and API usage

## Configuration:
The system accepts user inputs to customize analysis for specific contexts. These inputs help avoid false positives by recognizing personal information that might appear in passwords.

## Extension Points:
The modular design allows extension through:
- Adding new pattern matching strategies in the matching module
- Implementing alternative guess estimation algorithms in scoring
- Creating custom feedback generators
- Extending time estimation scenarios for new attack models

---

## Modules

- [`zxcvbn`](zxcvbn.md)

