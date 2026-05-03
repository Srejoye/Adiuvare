"""
LIVE RISK STREAM widget.
Scrollable table showing recent events with decision icons and dominant signal.
"""
from rich.text import Text
from textual.widgets import DataTable

from ..workspace import PALETTE, decision_color, decision_icon, dominant_color


class RiskStream(DataTable):
    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("", "SCORE", "VERDICT", "IDENTITY", "ENDPOINT", "DOMINANT")

    def show_events(self, events: list[dict]) -> None:
        self.clear(columns=False)
        for event in events:
            verdict = str(event.get("verdict", "allow"))
            score = float(event.get("score", 0))
            icon = decision_icon(verdict)
            color = decision_color(verdict)
            identity = str(event.get("identity", "?"))[:18]
            endpoint = str(event.get("endpoint", "?"))[:24]
            dominant = str(event.get("dominant", "-"))

            self.add_row(
                Text(f" {icon}", style=color),
                Text(f"{score:.4f}", style=PALETTE["cyan"]),
                Text(verdict, style=color),
                Text(identity, style=PALETTE["text"]),
                Text(endpoint, style=PALETTE["dim"]),
                Text(dominant, style=dominant_color(dominant)),
            )
