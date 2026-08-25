from dataclasses import dataclass
from enum import StrEnum


# Define the supported rules for when an on-screen game message should disappear.
class GameMessageDismissPolicy(StrEnum):
    ON_MOVE = "on_move"
    TIMED = "timed"


# Store the text to display and the rule that controls how long it remains visible.
@dataclass
class GameMessage:
    text: str
    dismiss_policy: GameMessageDismissPolicy

    # Timed messages may specify how many seconds they should remain visible.
    timeout_secs: float | None = None