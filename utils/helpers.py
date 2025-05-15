
import datetime
import time

def format_date(date):
    """Formats a datetime object to YYYY-MM-DD string."""
    return date.strftime('%Y-%m-%d')

def retry_on_failure(retries=3, delay=1):
    """Decorator to retry a function on failure."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(delay)
            raise Exception(f"All {retries} attempts failed.")
        return wrapper
    return decorator
