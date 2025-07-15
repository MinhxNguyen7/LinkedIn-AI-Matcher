import logging
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

# Global default log directory
DEFAULT_LOG_DIR = Path(".logs")


def create_logger(
    name: str,
    level: int = logging.INFO,
    log_dir: Path | None = DEFAULT_LOG_DIR,
    log_file: str | None = None,
    console_output: bool = True,
) -> logging.Logger:
    """
    Create a logger with optional file output and rich console formatting.

    Args:
        name: Logger name
        level: Logging level (default: INFO)
        log_dir: Directory for log files (default: DEFAULT_LOG_DIR)
        log_file: Optional log file name (if None, uses name.log)
        console_output: Whether to output to console (default: True)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler with rich formatting
    if console_output:
        console = Console()
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True,
        )
        console_handler.setLevel(level)
        logger.addHandler(console_handler)

    # File handler if log_dir is provided
    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)

        filename = log_file or f"{name}.log"
        log_path = log_dir / filename

        file_handler = logging.FileHandler(log_path, mode="a")
        file_handler.setLevel(level)

        # Simple format for file output
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
