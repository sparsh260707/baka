# utils.py
# Helper functions for BAKA Bot

def get_mention(user):
    """
    Returns an HTML mention of a user.
    Works with JSON DB structure:
    {
        "id": user_id,
        "name": "User",
        ...
    }
    """
    user_id = user.get("id")
    name = user.get("name", "User")
    return f'<a href="tg://user?id={user_id}">{name}</a>'
