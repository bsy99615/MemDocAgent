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
    Provides a robust, feature-complete IMAP client implementation with support for modern authentication methods, secure connections, and comprehensive response parsing.

## Description:
    The imapclient module serves as the core IMAP client implementation for interacting with IMAP servers. It provides a clean, Pythonic interface for common email operations such as connecting to mail servers, fetching messages, searching emails, and managing folders. This module handles the complexities of the IMAP protocol including authentication, secure connections (SSL/TLS), response parsing, and proper handling of various IMAP data types.

    The module is designed to be used by applications that need to interact with IMAP email servers programmatically. It's commonly used in email clients, email processing systems, and automated email management tools.

    Primary consumers of this module include:
    - Email processing applications
    - Automated email management systems
    - Email client libraries
    - Testing frameworks requiring IMAP connectivity

    The cohesion of this module is based on the shared concept of IMAP protocol handling and email client functionality. All components work together to provide a complete solution for IMAP communication, from low-level protocol handling to high-level convenience methods.

## Components:
    * config.py - Configuration management for IMAP connections including OAuth2 support
    * datetime_util.py - Utilities for converting between datetime objects and IMAP's INTERNALDATE format
    * fixed_offset.py - Timezone offset handling for IMAP date parsing
    * imap4.py - IMAP4 protocol implementation with timeout support
    * imap_utf7.py - UTF-7 encoding/decoding for IMAP mailbox names
    * interact.py - Interactive command-line interface for IMAP sessions
    * response_lexer.py - Lexical analysis of IMAP responses
    * response_parser.py - Parsing of IMAP server responses
    * response_types.py - Data types for IMAP responses
    * testable_imapclient.py - Mock implementations for testing purposes
    * tls.py - TLS/SSL handling for secure IMAP connections
    * util.py - Various utility functions for IMAP operations
    * version.py - Version information for the library

## Public API:
    * `config.create_client_from_config()` - Creates an IMAP client from configuration settings
    * `config.parse_config_file()` - Parses configuration files for IMAP settings
    * `datetime_util.datetime_to_INTERNALDATE()` - Converts datetime to IMAP INTERNALDATE format
    * `datetime_util.parse_to_datetime()` - Parses IMAP date strings to datetime objects
    * `fixed_offset.FixedOffset` - Timezone offset class for handling IMAP dates
    * `imap4.IMAP4WithTimeout` - IMAP4 implementation with configurable timeouts
    * `imap_utf7.encode()` - Encodes strings to IMAP UTF-7 format
    * `imap_utf7.decode()` - Decodes IMAP UTF-7 formatted strings
    * `interact.command_line()` - Command-line argument parsing for interactive mode
    * `response_parser.parse_fetch_response()` - Parses FETCH responses from IMAP server
    * `response_parser.parse_message_list()` - Parses message ID lists from IMAP server
    * `response_parser.parse_response()` - Parses general IMAP responses
    * `response_types.Address` - Represents email address information
    * `response_types.Envelope` - Represents email envelope information
    * `response_types.BodyData` - Represents email body structure information
    * `response_types.SearchIds` - Represents search results with optional modseq
    * `tls.IMAP4_TLS` - IMAP4 implementation with TLS support
    * `util.to_bytes()` - Converts strings to bytes with specified encoding
    * `util.to_unicode()` - Converts bytes to unicode strings

## Dependencies:
    * Internal imports:
        * `config` - Provides configuration management
        * `datetime_util` - Provides date/time conversion utilities
        * `fixed_offset` - Provides timezone handling
        * `imap4` - Provides IMAP4 protocol implementation
        * `imap_utf7` - Provides UTF-7 encoding/decoding
        * `interact` - Provides interactive CLI functionality
        * `response_lexer` - Provides lexical analysis for responses
        * `response_parser` - Provides parsing of IMAP responses
        * `response_types` - Provides data types for responses
        * `testable_imapclient` - Provides testable mock implementations
        * `tls` - Provides TLS/SSL handling
        * `util` - Provides general utility functions
        * `version` - Provides version information
    
    * External imports:
        * `argparse` - Command-line argument parsing
        * `configparser` - Configuration file parsing
        * `datetime` - Date and time handling
        * `imaplib` - Base IMAP library
        * `json` - JSON parsing for OAuth2 tokens
        * `logging` - Logging functionality
        * `os` - Operating system interface
        * `socket` - Network socket operations
        * `ssl` - Secure socket layer
        * `sys` - System-specific parameters
        * `time` - Time-related functions
        * `urllib.request` - URL request handling for OAuth2
        * `urllib.parse` - URL parsing for OAuth2
        * `email.utils` - Email utility functions (for formataddr)

## Constraints:
    * Callers must ensure proper IMAP server credentials are available before attempting to connect
    * When using OAuth2 authentication, valid client IDs, secrets, and refresh tokens must be provided
    * SSL/TLS connections require proper certificate validation setup when not using default settings
    * Response parsing assumes valid IMAP protocol responses; malformed responses may cause exceptions
    * Thread safety is not guaranteed for individual client instances - each thread should use its own client instance
    * Connection timeouts must be properly configured for network reliability
    * IMAP commands should be sent in the correct order according to the IMAP protocol specification

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

