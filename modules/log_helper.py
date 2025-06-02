import logging
import os

def setup_logger(name: str, log_file: str, level=logging.DEBUG) -> logging.Logger:
    """Creates a logger for each module with separate file and console handlers."""
    
    # Get the logger
    logger = logging.getLogger(name)
    
    # If logger is already configured, return it
    if logger.handlers:
        return logger
        
    # Set the logger level
    logger.setLevel(level)
    
    # Prevent propagation to root logger to avoid duplicate logs
    logger.propagate = False

    # Create log directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # File handler (all details to file)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)  # Log everything to file
    file_format = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] %(message)s')
    file_handler.setFormatter(file_format)

    # Console handler (only INFO, ERROR, and EXCEPTION)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Only show INFO and above in console
    # Show level and message in console for better visibility
    console_format = logging.Formatter('[%(levelname)s] %(message)s')
    console_handler.setFormatter(console_format)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
