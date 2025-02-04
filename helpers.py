from functools import wraps
from flask import redirect, session

# Function to check if user is logged in
def login_required(f):
    @wraps(f)

    def decorated_function(*args, **kwargs):

        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    
    return decorated_function
