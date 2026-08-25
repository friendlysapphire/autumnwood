from dataclasses import dataclass, field
from enum import StrEnum

DEFAULT_TIMEOUT_SECS = 3.0

# Define the supported rules for when an on-screen game message should disappear.
class GameMessageDismissPolicy(StrEnum):
    ON_MOVE_ATTEMPT = "on_move_attempt"
    TIMED = "timed"


# Store the text to display and the rule that controls how long it remains visible.
@dataclass
class GameMessage:
    text: str
    dismiss_policy: GameMessageDismissPolicy

    # Timed messages may specify how many seconds they should remain visible.
    timeout_secs: float | None = None
    remaining_secs: float | None = field(init=False)

    def __post_init__(self) -> None:

        if (
            self.dismiss_policy == GameMessageDismissPolicy.TIMED and 
            (self.timeout_secs is None or self.timeout_secs <= 0)
        ):
            self.timeout_secs = DEFAULT_TIMEOUT_SECS

        self.remaining_secs = self.timeout_secs

