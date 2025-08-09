# agents/auth_agent.py
from auth.jwt_auth import decode_token, get_current_user

def auth_agent(state):
    """
    Expects state to contain 'jwt' key (the Bearer token string).
    Returns state with 'user' added if token valid, else raises/returns error.
    """
    token = state.get("jwt")
    if not token:
        return {"error": "missing_token", "authorized": False}

    user = get_current_user(token)
    if not user:
        return {"error": "invalid_token", "authorized": False}
    # authorized, attach user
    return {**state, "user": user, "authorized": True}
