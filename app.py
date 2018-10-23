from bokeh.embed import components
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.palettes import viridis
from bokeh.plotting import figure
from bokeh.resources import INLINE
from flask import flash, Flask, redirect, render_template, request, url_for
import math
import os
import time

import config
from reddit_data import get_posts, get_time_filter_expression, is_valid_subreddit_name
from util import epoch2decimal, round_up_by, sanitize

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/", methods=["GET", "POST"])
def index():
    success = False
    if request.method == "POST":
        subreddit = sanitize(request.form.get("subreddit"))
        if subreddit=="":
            subreddit = "all"

        # Check if the input matches the subreddit naming conventions
        if not is_valid_subreddit_name(subreddit):
            flash("Requested subreddit was invalid.")
            return redirect(url_for("index"))

        # TODO: Expose these as options
        limit = 500
        time_filter = "year"

        # Check if the requested subreddit exists; if so, get that subreddit's posts
        try:
            posts = get_posts(subreddit, limit=limit, time_filter=time_filter)
        except Exception as e:
            flash("Requested subreddit does not exist.")
            return redirect(url_for("index"))

        success = True

        # Data
        formatted_times = [time.strftime("%H:%M:%S", time.localtime(post.created_utc)) for post in posts]
        hours = [math.floor(epoch2decimal(t)) for t in formatted_times]
        y = list(range(24))
        
        ylabels = [((str(i % 12) if (i % 12 != 0) else str(12)) + (" am" if i < 12 else " pm")) for i in y]
        x = [hours.count(i) for i in y]

        # 0 - Hours (y-axis)
        # 1 - Number of posts (x-axis)
        # 2 - Hour strings e.g. "12 pm"
        unsorted_data = list(zip(y, x, ylabels))

        # 0.5 offset to align the horizontal bars to their respective y_range label
        y = [(i + 0.5) for i in y]

        # ===== f1 (unsorted) ======
        source1 = ColumnDataSource(data=dict(xvals=x, yvals=y, textvals=[x if x != "0" else "" for x in list(map(str, x))]))

        f1 = figure(tools="", x_range=(0, round_up_by(max(x), max(x) + max(x) / 5 + 1)), y_range=ylabels)
        f1.hbar(y=y, height=0.95, left=0, right=x, fill_color="#4292c6", line_color="#084594")

        f1.xgrid.grid_line_alpha=0.4
        f1.ygrid.grid_line_alpha=0.4

        labels1 = LabelSet(x="xvals", y="yvals", text="textvals", level="glyph", x_offset=5, y_offset=-5, source=source1, render_mode="canvas", text_font_size="8pt")
        f1.add_layout(labels1)

        f1.title.text = "r/" + subreddit + " Submission Time/Upvote Correlation"
        f1.xaxis.axis_label = "Number of Posts"
        f1.yaxis.axis_label = "Local Time"

        # ===== f2 (sorted) ======
        # Sort the list of tuples based on the number of posts
        sorted_data = sorted(unsorted_data, key=lambda x: x[1])
        right = ([i[1] for i in sorted_data])
        best_time = sorted_data[len(sorted_data) - 1][2]
        print("Best time: " + best_time)

        viridis256 = viridis(256)
        colors = [viridis256[int(i / (max(right)) * 255) if max(right) != 0 else 0] for i in right]

        source2 = ColumnDataSource(data=dict(right=right, y=y, textvals=[x if x != "0" else "" for x in list(map(str, right))], colors=colors))

        f2 = figure(tools="", x_range=(0, round_up_by(max(x), max(x) + max(x) / 5 + 1)), y_range=[i[2] for i in sorted_data])
        f2.hbar(y="y", height=0.95, left=0, right="right", source=source2, fill_color="colors")

        f2.xgrid.grid_line_alpha=0.4
        f2.ygrid.grid_line_alpha=0.4

        labels2 = LabelSet(x="right", y="y", text="textvals", level="glyph", x_offset=5, y_offset=-5, source=source2, render_mode="canvas", text_font_size="8pt")
        f2.add_layout(labels2)

        f2.title.text = "r/" + subreddit + " Submission Time/Upvote Correlation (Sorted)"
        f2.xaxis.axis_label = "Number of Posts"
        f2.yaxis.axis_label = "Local Time"

        # gridplot
        p = gridplot([[f1, f2]], toolbar_location=None)

        # Embed plot
        js_resources = INLINE.render_js()
        css_resources = INLINE.render_css()
        script, div = components(p)

        return render_template("index.html",
            success=success,
            subreddit=subreddit,
            limit=limit,
            time_filter=get_time_filter_expression(time_filter),
            script=script,
            div=div,
            js_resources=js_resources,
            css_resources=css_resources,
            best_time=best_time)

    return render_template("index.html")

if __name__ == "__main__":
    app.run()
