from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class UIState:
    username: str = ""
    debug_mode: bool = False

    instrument_connected: bool = False
    server_status: str = "Disconnected"

    blank_file_path: Optional[str] = None
    sample_files: List[str] = field(default_factory=list)

    offline_mode: bool = False
