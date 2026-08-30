from dataclasses import dataclass
from enum import StrEnum

import pygame

DEFAULT_TIMEOUT_SECS = 3.0

# Define the supported rules for when an on-screen game notification should disappear.
class GameNotificationDismissPolicy(StrEnum):
    ON_MOVE_ATTEMPT = "on_move_attempt"
    TIMED = "timed"


# Describe a notification's text and dismissal rule. NotificationPanel owns the
# active-notification lifecycle state, including the remaining display time.
@dataclass
class GameNotification:
    text: str
    dismiss_policy: GameNotificationDismissPolicy

    # Timed notifications may specify how many seconds they should remain visible.
    timeout_secs: float | None = None

    def __post_init__(self) -> None:

        if (
            self.dismiss_policy == GameNotificationDismissPolicy.TIMED and 
            (self.timeout_secs is None or self.timeout_secs <= 0)
        ):
            self.timeout_secs = DEFAULT_TIMEOUT_SECS

class NotificationPanel:

    def __init__(self,
                 *,
                 screen: pygame.Surface,
                 panel_width:int,
                 panel_height:int,
                 window_height: int,
                 alpha:int = 100,
                 font: pygame.font.Font | None = None
                 ) -> None:
        
        self.panel_width = panel_width
        self.panel_height = panel_height
        self.window_height = window_height
        self.panel_alpha = alpha
        self.screen = screen

        if font is None:
            self.font = pygame.font.Font(None, 22)
        else:
            self.font = font

        # This transparent Surface is redrawn only when an active notification exists.
        self.notification_panel = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        self.notification_panel.fill((0, 0, 0, self.panel_alpha))

        # Track the notification currently presented by this panel.
        self.current_notification: GameNotification | None = None

        # Timed notifications keep their countdown here rather than in GameNotification.
        self.remaining_secs: float | None = None

    def set_notification(self, notification: GameNotification) -> None:
        self.current_notification = notification

        if self.current_notification.dismiss_policy == GameNotificationDismissPolicy.TIMED:
            self.remaining_secs = self.current_notification.timeout_secs
        elif self.current_notification.dismiss_policy == GameNotificationDismissPolicy.ON_MOVE_ATTEMPT:
            self.remaining_secs = None

    # Advance timed-notification lifecycle, then draw the active notification for this frame.
    def update_and_draw(self, delta_secs: float) -> None:

        # Count down timed notifications and clear them when their display time expires.
        if (self.current_notification is not None and 
            self.current_notification.dismiss_policy == GameNotificationDismissPolicy.TIMED
            ):

            assert self.remaining_secs is not None
            self.remaining_secs -= delta_secs

            if self.remaining_secs <= 0:
                self.current_notification = None
                self.remaining_secs = None

        # Draw only after expiration processing so an expired notification is not rendered.
        if self.current_notification is not None:
            self._draw()

    def notify_move_attempted(self) -> None:

        if (self.current_notification is not None and 
            self.current_notification.dismiss_policy == GameNotificationDismissPolicy.ON_MOVE_ATTEMPT
            ):

            self.current_notification = None

    def _draw(self) -> None:

        if self.current_notification is not None:
            # Clear previous notification text before drawing the active notification.
            self.notification_panel.fill((0, 0, 0, self.panel_alpha))

            notification_surface = self.font.render(self.current_notification.text, True, "grey87")
            self.notification_panel.blit(notification_surface, (20,20)) 
            self.screen.blit(self.notification_panel, (20, self.window_height - self.panel_height))


        
                
    

    
