"""
Progress tracking utilities for the translator program.
"""
from typing import Iterable, TypeVar, Iterator, Optional, Callable

T = TypeVar('T')


class ProgressTracker:
    """
    A utility class for tracking progress of operations.
    
    This class provides a way to track progress of operations like translation
    with support for different progress bar implementations.
    """
    
    def __init__(self):
        """Initialize the progress tracker."""
        self._tqdm = None
        
    def track(self, iterable: Iterable[T], total: Optional[int] = None, 
              desc: str = "Progress", **kwargs) -> Iterator[T]:
        """
        Wrap an iterable with a progress bar.
        
        Args:
            iterable: The iterable to track progress for.
            total: The total number of items (optional if iterable has __len__).
            desc: Description for the progress bar.
            **kwargs: Additional arguments to pass to the progress bar.
            
        Returns:
            An iterator that yields items from the input iterable while updating the progress bar.
        """
        try:
            # Import tqdm here to avoid dependency issues if not installed
            from tqdm import tqdm
            self._tqdm = tqdm
        except ImportError:
            # Fallback to a simple progress tracker if tqdm is not available
            return self._simple_tracker(iterable, total, desc)
        
        return self._tqdm(iterable, total=total, desc=desc, **kwargs)
    
    def _simple_tracker(self, iterable: Iterable[T], total: Optional[int] = None, 
                        desc: str = "Progress") -> Iterator[T]:
        """
        A simple progress tracker that prints progress to the console.
        
        Args:
            iterable: The iterable to track progress for.
            total: The total number of items.
            desc: Description for the progress.
            
        Returns:
            An iterator that yields items from the input iterable while printing progress.
        """
        if total is None:
            try:
                total = len(iterable)
            except (TypeError, AttributeError):
                # If we can't determine the total, just yield the items
                for item in iterable:
                    yield item
                return
        
        count = 0
        for item in iterable:
            yield item
            count += 1
            if count % max(1, total // 10) == 0 or count == total:
                percent = (count / total) * 100
                print(f"{desc}: {count}/{total} ({percent:.1f}%)")
                
    def update_message(self, message: str) -> None:
        """
        Update the progress bar message.
        
        Args:
            message: The new message to display.
        """
        if self._tqdm:
            self._tqdm.write(message)
        else:
            print(message)