import re

def get_hour(hour):
    return 12 if hour == 0 or hour == 12 else hour % 12

def get_meridiem(hour):
    return "am" if 0 <= hour < 12 else "pm"

def get_12_hour_time(hour):
    return f"{get_hour(hour)} {get_meridiem(hour)}"

def sanitize(name, pattern=r"[^\w]", repl=""):
    # Check for characters that are neither alphanumeric nor an underscore
    return re.sub(pattern, repl, name)
