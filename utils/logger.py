import sys
from loguru import logger

# Remove default logger
logger.remove()

# Add a clean, informative stdout logger
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:sc}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
    colorize=True,
)

# Optional: Add file logging
logger.add(
    "logs/synapse.log",
    rotation="10 MB",
    retention="10 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)
