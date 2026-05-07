# `imapclient`

## Tree:
    imapclient/
    ├── config.py
    ├── datetime_util.py
    ├── fixed_offset.py
    ├── imap4.py
    ├── imap_utf7.py
    ├── interact.py
    ├── response_lexer.py
    ├── response_parser.py
    ├── response_types.py
    ├── testable_imapclient.py
    ├── tls.py
    ├── util.py
    └── version.py

## Role:
    Provides core IMAP client functionality for email server communication.

## Description:
    The imapclient module implements a comprehensive IMAP client library that enables applications to communicate with IMAP email servers. It offers functionality for connecting to mail servers, authenticating users, managing folders, searching messages, and retrieving email content.

    This module is organized into several logical components that work together to provide a complete IMAP client implementation. The design emphasizes modularity, with separate concerns for connection handling, protocol parsing, response processing, and utility functions.

    The module is intended for use in applications that require reliable email server interaction, including email clients, synchronization services, and automated email processing systems.

## Components:
    * config.py - Configuration handling utilities
    * datetime_util.py - Date/time utility functions
    * fixed_offset.py - Timezone offset handling
    * imap4.py - Core IMAP protocol implementation
    * imap_utf7.py - UTF-7 encoding/decoding utilities
    * interact.py - Interactive client interface
    * response_lexer.py - Response tokenization
    * response_parser.py - Response parsing
    * response_types.py - Response data types
    * testable_imapclient.py - Testable IMAP client wrapper
    * tls.py - TLS/SSL connection handling
    * util.py - General utility functions
    * version.py - Version information

## Public API:
    * imap4.IMAPClient - Main IMAP client class for server communication
    * response_parser.parse_response() - Function to parse IMAP responses
    * response_lexer.lexer() - Function to tokenize IMAP responses
    * response_types.ResponseType - Data type definitions for responses
    * tls.start_tls() - Function to establish secure connections
    * util.format_date() - Utility for date formatting
    * datetime_util.parse_date() - Utility for date parsing

## Dependencies:
    * Internal: Components within the imapclient package depend on each other to form a cohesive IMAP client implementation
    * External: Standard library modules (socket, ssl, datetime, logging) for core functionality

## Constraints:
    * Connections must be properly established before sending commands
    * IMAP protocol compliance is required for valid operations
    * Secure connections should use TLS when available
    * Thread safety considerations apply to connection usage

---

## Files

- [`config.py`](imapclient/config.md)
- [`datetime_util.py`](imapclient/datetime_util.md)
- [`fixed_offset.py`](imapclient/fixed_offset.md)
- [`imap4.py`](imapclient/imap4.md)
- [`imap_utf7.py`](imapclient/imap_utf7.md)
- [`interact.py`](imapclient/interact.md)
- [`response_lexer.py`](imapclient/response_lexer.md)
- [`response_parser.py`](imapclient/response_parser.md)
- [`response_types.py`](imapclient/response_types.md)
- [`testable_imapclient.py`](imapclient/testable_imapclient.md)
- [`tls.py`](imapclient/tls.md)
- [`util.py`](imapclient/util.md)
- [`version.py`](imapclient/version.md)

