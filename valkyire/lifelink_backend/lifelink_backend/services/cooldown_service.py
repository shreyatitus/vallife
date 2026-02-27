from datetime import datetime, timedelta
from config import COOLDOWN_DAYS

def is_eligible(donor):
    if donor.last_donation is None:
        return True

    next_available = donor.last_donation + timedelta(days=COOLDOWN_DAYS)
    return datetime.now() >= next_available