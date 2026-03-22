import sys
from pathlib import Path
from loguru import logger

def setup_logger(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.remove()

    file_fmt = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {module}:{function}:{line} - {message}"

    console_fmt = "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{module}</cyan> - <level>{message}</level>"

    logger.add(
        output_dir / "app.log",
        rotation="1 MB",
        encoding="utf-8",
        format=file_fmt,
        level="DEBUG",
    )

    logger.add(
        output_dir / "errors.log",
        rotation="1 MB",
        encoding="utf-8",
        format=file_fmt,
        level="ERROR",
        backtrace=True,
        diagnose=True,
    )

    logger.add(sys.stderr, format=console_fmt, level="INFO")