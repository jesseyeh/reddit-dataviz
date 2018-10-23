import re

def epoch2decimal(time):
    (h, m, s) = time.split(":")
    return (int(h) + int(m) / 60 + int(s) / 3600)

def round_up_by(num, multiple_to_round_up_by):
    return ((-num // multiple_to_round_up_by) * -multiple_to_round_up_by) 

def sanitize(name, pattern=r"[^\w]", repl=""):
    # Check for characters that are neither alphanumeric nor an underscore
    return re.sub(pattern, repl, name)
