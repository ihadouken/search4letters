from flask import session
from functools import wraps
def check_status(func: object) -> object:
    """This Decorator protects the argumented function from unauthorized
    access by 'checking' if the user is authorized"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Needless to say, this nested function wraps extra code around the argumented function
        and hence its name."""

        if 'logged_in' in session:        # decorated function 'func' is invoked only if the user is logged in. 
            return func(*args, **kwargs)  # wrapper' must have the sigature as of decorated function as it has to return it.

        return 'You are NOT logged in.'
    
    return wrapper # 'check_status' returns the 'wrapper' function's object.
