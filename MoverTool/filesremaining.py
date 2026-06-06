"""
Custom class used to track the number of files remaining in a directory. This class is used in the main script to keep
track of how many files are left to process and to update the progress bar accordingly.
"""
from rich.progress import ProgressColumn
from rich.text import Text


class FilesRemainingColumn(ProgressColumn):
    """Custom column showing number of files remaining."""

    def render(self, task) -> Text:
        try:
            remaining = int(task.total - task.completed) if task.total else 0
        except Exception:
            remaining = 0
        return Text(f"{remaining} files remaining")
