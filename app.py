from flask import flash, Flask, redirect, render_template, request, url_for
import pandas as pd
import os
import time

import config
import constants
from reddit_data import get_posts, is_valid_subreddit_name
from util import get_12_hour_time, sanitize

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/", methods=["GET", "POST"])
def index():
    success = False

    if request.method == "POST":
        # Process user input
        sample_size = sanitize(request.form.get("sample_size"), constants.NON_NUMERIC_PATTERN)
        if not sample_size or not int(sample_size) in constants.SAMPLE_SIZES:
            sample_size = constants.DEFAULT_SAMPLE_SIZE
        else:
            sample_size = int(sample_size)

        time_range = sanitize(request.form.get("time_range"), constants.NON_ALPHA_NON_SPACE_PATTERN)
        if not time_range or not time_range in constants.TIME_RANGES:
            time_range = constants.DEFAULT_TIME_RANGE

        subreddit = sanitize(request.form.get("subreddit"), constants.NON_ALPHANUMERIC_PATTERN)
        if not subreddit:
            subreddit = constants.DEFAULT_SUBREDDIT

        # Check if the input matches the subreddit naming conventions
        if not is_valid_subreddit_name(subreddit):
            flash("Requested subreddit was invalid.")
            return redirect(url_for("index"))

        limit = sample_size
        time_filter = constants.TIME_RANGES[time_range]

        # Check if the requested subreddit exists; if so, get that subreddit's posts
        try:
            posts = get_posts(subreddit, limit=limit, time_filter=time_filter)
        except Exception as e:
            flash("Requested subreddit does not exist.")
            return redirect(url_for("index"))

        success = True

        # Data
        df = pd.DataFrame({"id": [post.id for post in posts],
                           "hour": [(pd.to_datetime(post.created_utc, unit="s").hour) for post in posts]})

        valcounts_df = pd.DataFrame(df["hour"].value_counts().reset_index())
        valcounts_df.columns = ["hour", "count"]

        chron_df = valcounts_df.sort_values(by=["hour"])

        valcounts_data = valcounts_df.to_dict(orient="records")
        chron_data = chron_df.to_dict(orient="records")

        return render_template("index.html",
            success=success,
            subreddit=subreddit,
            sample_size=sample_size,
            sample_sizes=constants.SAMPLE_SIZES,
            time_range=time_range,
            time_ranges=constants.TIME_RANGES.keys(),
            limit=min(limit, valcounts_df["count"].sum()),
            time_range_expression=constants.TIME_RANGE_EXPRESSIONS[time_range],
            valcounts_data=valcounts_data,
            valcounts_title="r/" + subreddit + " " + constants.VALCOUNTS_TITLE,
            chron_data=chron_data,
            chron_title="r/" + subreddit + " " + constants.CHRON_TITLE)

    return render_template("index.html",
        sample_size=constants.DEFAULT_SAMPLE_SIZE,
        sample_sizes=constants.SAMPLE_SIZES,
        time_range=constants.DEFAULT_TIME_RANGE,
        time_ranges=constants.TIME_RANGES.keys())

if __name__ == "__main__":
    app.run()
