from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class UIState:
    username: str = ""
    debug_mode: bool = False

    instrument_connected: bool = True
    server_status: str = "OK"

    blank_file_path: Optional[str] = None
    sample_files: List[str] = field(default_factory=list)