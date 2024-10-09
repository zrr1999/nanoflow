from __future__ import annotations

from typing import ClassVar

from textual.app import App, Binding, BindingType, ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Footer, Label, Markdown, RichLog, TabbedContent, Tabs

from .config import WorkflowConfig


class HelpScreen(ModalScreen[None]):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("q", "app.quit", "Quit", show=False),
        Binding("escape,f1,?", "app.pop_screen()", "Close help", key_display="esc"),
    ]

    HELP_MARKDOWN = """\
### How do I quit the app?

Press `Ctrl+C` on your keyboard.
`q` also works if an input isn't currently focused.
"""

    def compose(self) -> ComposeResult:
        with Vertical(id="help-container") as vertical:
            vertical.border_title = "Help"
            with VerticalScroll():
                yield Markdown(self.HELP_MARKDOWN, id="help-markdown")
            yield Markdown(
                "Use `pageup`, `pagedown`, `up`, and `down` to scroll.",
                id="help-scroll-keys-info",
            )
        yield Footer()


class Nanoflow(App[None]):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("d", "toggle_dark", "Toggle dark mode"),
        Binding("q", "app.quit", "Quit", show=False),
        Binding("f1,?", "help", "Help"),
    ]

    def __init__(self, workflow_config: WorkflowConfig):
        super().__init__()
        self.workflow_config = workflow_config

    def update_log(self, task_name: str, line: bytes):
        if self.is_running:
            self.query_one(f"#log-{task_name}", RichLog).write(line.decode())

    def compose(self) -> ComposeResult:
        with TabbedContent(*list(self.workflow_config.tasks.keys())):
            for task_name in self.workflow_config.tasks:
                yield RichLog(id=f"log-{task_name}")
        yield Footer()

    def on_mount(self) -> None:
        """Focus the tabs when the app starts."""
        self.query_one(Tabs).focus()

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle TabActivated message sent by Tabs."""
        label = self.query_one(Label)
        label.visible = True
        label.update(event.tab.label)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    async def action_help(self) -> None:
        if isinstance(self.screen, HelpScreen):
            self.pop_screen()
        else:
            await self.push_screen(HelpScreen())
