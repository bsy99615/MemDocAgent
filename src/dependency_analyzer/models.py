"""
Shared data models for multilanguage code analysis.

Node and CallRelationship are used by all language-specific analyzers
as the common output format.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Set


@dataclass
class Node:
    """Represents a single code component extracted by a language analyzer."""
    id: str
    name: str
    component_type: str
    file_path: str
    relative_path: str
    depends_on: Set[str] = field(default_factory=set)
    source_code: Optional[str] = None
    start_line: int = 0
    end_line: int = 0
    has_docstring: bool = False
    docstring: str = ""
    parameters: Optional[List[str]] = None
    node_type: Optional[str] = None
    base_classes: Optional[List[str]] = None
    class_name: Optional[str] = None
    display_name: Optional[str] = None
    component_id: Optional[str] = None

    def get_display_name(self) -> str:
        return self.display_name or self.name


@dataclass
class CallRelationship:
    """Represents a call relationship between two code components."""
    caller: str
    callee: str
    call_line: Optional[int] = None
    is_resolved: bool = False
