NON_NUMERIC_PATTERN = r"\D"
NON_ALPHA_NON_SPACE_PATTERN = r"[^A-Za-z ]"
NON_ALPHANUMERIC_PATTERN = r"\W"

DEFAULT_SAMPLE_SIZE = 100
SAMPLE_SIZES = [1000, 500, 100, 50, 10]

ALL_TIME = "All Time"
PAST_YEAR = "Past Year"
PAST_MONTH = "Past Month"
PAST_WEEK = "Past Week"
PAST_DAY = "Past Day"
DEFAULT_TIME_RANGE = PAST_YEAR
TIME_RANGES = {ALL_TIME:"all", PAST_YEAR:"year", PAST_MONTH:"month", PAST_WEEK:"week", PAST_DAY:"day"}
TIME_RANGE_EXPRESSIONS = {ALL_TIME:"all time", PAST_YEAR:"the past year", PAST_MONTH:"the past month", PAST_WEEK:"the past week", PAST_DAY:"the past day"}

DEFAULT_SUBREDDIT = "all"

VALCOUNTS_TITLE = "Submission Upvote/Time Correlation (Sorted)"
CHRON_TITLE = "Submission Upvote/Time Correlation"
