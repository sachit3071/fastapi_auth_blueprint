import logging

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)


# decorator to log function calls
def log_function_call(func):
    def wrapper(*args, **kwargs):
        try:
            # logging with function name and parent classes
            logger.info(
                f"Calling {func.__module__}.{func.__name__} with args {args} and kwargs {kwargs}"
            )
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__module__}.{func.__name__}: {str(e)}")
            raise

    return wrapper
