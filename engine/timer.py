# ========== IMPORT ==========
from datetime import datetime, timedelta
from engine.ghost import load_ghosts, check_and_process_ghosts, get_all_ghosts

# ========== CHECK ==========
def check_expired_ghosts():
    """
    Runs the full check (expiration + dead man switch + soft/hard destruction).
    Call this at application startup.
    """
    return check_and_process_ghosts()

# ========== GET ACTIVE ==========
def get_active_ghosts() -> dict:
    """Return only active ghosts."""
    ghosts = get_all_ghosts()
    return {name: data for name, data in ghosts.items() if data.get("status") == "active"}

# ========== TIME REMAINING ==========
def get_time_remaining(name: str) -> str | None:
    """
    Returns the remaining time before expiration in a readable format.
    Example: "3 days", "12 hours", "Expired"
    """
    ghosts = load_ghosts()
    if name not in ghosts:
        return None

    ghost = ghosts[name]
    if ghost.get("status") != "active":
        return "Destroyed / Expired"

    try:
        expire_date = datetime.strptime(ghost["expire_date"], "%Y-%m-%d")
        now = datetime.now()

        if now.date() > expire_date.date():
            return "Expired"

        delta = expire_date - now
        days = delta.days
        hours = delta.seconds // 3600

        if days > 0:
            return f"{days} day{'s' if days > 1 else ''}"
        elif hours > 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            return "Less than an hour"
    except Exception:
        return None

# ========== DEAD MAN REMAINING ==========
def get_dead_man_remaining(name: str) -> str | None:
    """
    Remaining time before destruction by dead man switch.
    """
    ghosts = load_ghosts()
    if name not in ghosts:
        return None

    ghost = ghosts[name]
    if not ghost.get("dead_man_days") or ghost.get("status") != "active":
        return None

    try:
        last_activity = datetime.strptime(ghost["last_activity"], "%Y-%m-%d %H:%M:%S")
        deadline = last_activity + timedelta(days=ghost["dead_man_days"])
        now = datetime.now()

        if now >= deadline:
            return "Expired (dead man switch)"

        delta = deadline - now
        days = delta.days
        return f"{days} day{'s' if days > 1 else ''} remaining"
    except Exception:
        return None