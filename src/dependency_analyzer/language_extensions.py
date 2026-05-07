"""
File extension to language name mapping for multilanguage support.

Only languages with implemented analyzers are included.
"""

# Maps file extension to language identifier used by analyzer dispatch
CODE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".java": "java",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".c++": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".hxx": "cpp",
    ".h++": "cpp",
    ".php": "php",
    ".kt": "kotlin",
    ".cs": "csharp",
}
