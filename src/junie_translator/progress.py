"""
Progress bar module for showing translation progress.
"""

from typing import Optional, Callable, Any

from tqdm import tqdm


class ProgressTracker:
    """
    Progress tracker for showing translation progress.
    """

    def __init__(self, total: int, description: str = "Translating"):
        """
        Initialize the progress tracker.

        Args:
            total: Total number of items to process
            description: Description to show in the progress bar
        """
        self.progress_bar = tqdm(
            total=total,
            desc=description,
            unit="lines",
            ncols=100,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
        )

    def update(self, n: int = 1) -> None:
        """
        Update the progress bar.

        Args:
            n: Number of items to increment by
        """
        self.progress_bar.update(n)

    def close(self) -> None:
        """
        Close the progress bar.
        """
        self.progress_bar.close()

    def __enter__(self):
        """
        Context manager entry.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.
        """
        self.close()


def with_progress(
    items: list,
    process_func: Callable[[Any], Any],
    description: str = "Processing"
) -> list:
    """
    Process items with a progress bar.

    Args:
        items: List of items to process
        process_func: Function to process each item
        description: Description to show in the progress bar

    Returns:
        List of processed items
    """
    results = []
    with ProgressTracker(total=len(items), description=description) as progress:
        for item in items:
            result = process_func(item)
            results.append(result)
            progress.update()
    return results