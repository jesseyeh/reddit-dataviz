class Chart {
    constructor(data, title) {
        this.data = data;
        this.title = title;
    }
}

const margin = {top: 30, right: 60, bottom: 60, left: 70};
const svgWidth = 800;
const svgHeight = 600;
const graphWidth = svgWidth - margin.left - margin.right;
const graphHeight = svgHeight - margin.top - margin.bottom;

const timezoneOffset = new Date().getTimezoneOffset() / 60;

var xScale = d3.scaleLinear()
    .range([0, graphWidth])

var yScale = d3.scaleBand()
    .range([0, graphHeight])

// https://github.com/d3/d3-scale-chromatic
function getColors(specifier) {
    // Floor n with a bitwise OR
    var n = specifier.length / 6 | 0, colors = new Array(n), i = 0;
    while (i < n) colors[i] = "#" + specifier.slice(i * 6, ++i * 6);
    return colors;
}

function ramp(range) {
    var n = range.length;
    return function(t) {
        return range[Math.max(0, Math.min(n - 1, Math.floor(t * n)))];
    };
}

// https://stackoverflow.com/questions/24784302/wrapping-text-in-d3
function wrap(text, width) {
    text.each(function () {
        var text = d3.select(this),
            words = text.text().split(/\s+/).reverse(),
            word,
            line = [],
            lineNumber = 0,
            lineHeight = 1.1,
            x = text.attr("x"),
            y = text.attr("y"),
            dy = 0,
            tspan = text.text(null)
                        .append("tspan")
                        .attr("x", x)
                        .attr("y", y)
                        .attr("dy", dy + "em");

        while (word = words.pop()) {
            line.push(word);
            tspan.text(line.join(" "));
            if (tspan.node().getComputedTextLength() > width) {
                line.pop();
                tspan.text(line.join(" ").concat(" "));
                line = [word];
                tspan = text.append("tspan")
                            .attr("x", x)
                            .attr("y", y)
                            .attr("dy", ++lineNumber * lineHeight + dy + "em")
                            .text(word);
            }
        }
    });
}

function getHour(hour) {
    return (hour % 12 == 0) ? 12 : hour % 12;
}

function getMeridiem(hour) {
    return (0 <= hour && hour < 12) ? "am" : "pm";
}

function getTime(hour, offset=0) {
    var localHour = (hour - offset + 24) % 24;
    return `${ getHour(localHour) } ${ getMeridiem(localHour) }`;
}

function drawChart(chart, svg, colors) {
    data = chart.data;
    title = chart.title;

    xScale.domain([0, d3.max(data, function(d) { return d.count; })]);
    yScale.domain(data.map(function(d) { return d.hour; }));

    var colorscheme = d3.scaleSequential()
        .domain([0, d3.max(data, function(d) { return d.count; })])
        .interpolator(ramp(getColors(colors)));

    // Draw x-axis
    svg.append("g")
        .attr("class", "xaxis")
        .attr("transform", `translate(0, ${graphHeight})`)
        .call(d3.axisBottom(xScale)
            .ticks(Math.min(xScale.ticks().length, xScale.domain()[1])));

    // Draw y-axis
    svg.append("g")
        .attr("class", "yaxis")
        .call(d3.axisLeft(yScale)
            .tickFormat(function(d) { return getTime(d, timezoneOffset); }));

    // Draw horizontal grid lines
    svg.append("g")
        .attr("class", "xgrid")
        .call(d3.axisLeft(yScale)
            .tickSize(-graphWidth, 0, 0)
            .tickFormat(""));

    // Draw vertical grid lines
    svg.append("g")
        .attr("class", "ygrid")
        .attr("transform", "translate(0, " + graphHeight + ")")
        .call(d3.axisBottom(xScale)
            .tickSize(-graphHeight, 0, 0)
            .tickFormat(""));

    // Draw chart title
    svg.append("text")
        .attr("class", "chartTitle")
        .text(title)
        .attr("x", 0)
        .attr("y", function() { return -margin.top + this.getBBox().height; })
        .call(wrap, graphWidth);

    // Draw bars
    svg.selectAll("bar")
        .data(data)
        .enter()
        .append("rect")
            .attr("class", "bar")
            .attr("x", 0)
            .attr("y", (d) => yScale(d.hour))
            .attr("height", yScale.bandwidth())
            .attr("width", (d) => xScale(d.count))
            .attr("fill", function(d) { return colorscheme(d.count); });

    // Draw text for each bar
    svg.selectAll("bartext")
        .data(data)
        .enter()
        .append("text")
            .attr("class", "bartext")
            .text(function(d) { return d.count; })
            .attr("x", function(d) { return xScale(d.count) + (this.getBBox().width / 3); })
            .attr("y", function(d) { return yScale(d.hour) + yScale.bandwidth() / 2 + (this.getBBox().height / 3); });

    // Draw x-axis label
    svg.append("text")
        .attr("class", "xaxislabel")
        .text("Number of Posts")
        .attr("x", graphWidth / 2)
        .attr("y", function() { return graphHeight + margin.bottom - this.getBBox().height; });

    // Draw y-axis label
    svg.append("text")
        .attr("class", "yaxislabel")
        .text("Local Time")
        .attr("transform", "rotate(-90)")
        .attr("x", 0 - graphHeight / 2)
        .attr("y", function() { return 0 - margin.left + this.getBBox().height; });
}

function resize(container, chart) {
    var width = parseInt(container.style("width")) - margin.left - margin.right;
    var height = parseInt(container.style("height")) - margin.top - margin.bottom;

    // Update scale ranges
    xScale.range([0, width]);
    yScale.range([0, height]);
    yScale.domain(chart.data.map(function(d) { return d.hour; }));

    // Update x-axis
    container.select(".xaxis")
        .attr("transform", "translate(0, " + height + ")")
        .call(d3.axisBottom(xScale)
            .ticks(Math.min(xScale.ticks().length, xScale.domain()[1])));

    // Update x-axis label
    container.select(".xaxislabel")
        .attr("x", width / 2)
        .attr("y", function() { return height + margin.bottom - this.getBBox().height; });

    // Update y-axis label
    container.select(".yaxis")
        .call(d3.axisLeft(yScale)
            .tickFormat(function(d) { return getTime(d, timezoneOffset); }));

    // Update horizontal grid lines
    container.select(".xgrid")
        .call(d3.axisLeft(yScale)
            .tickSize(-width)
            .tickFormat(""));

    // Update chart title
    container.select(".chartTitle")
        .call(wrap, width);

    // Update vertical grid lines
    container.select(".ygrid")
        .call(d3.axisBottom(xScale)
            .tickSize(-height)
            .tickFormat(""));

    // Update bar text
    container.selectAll(".bartext")
        .attr("x", function(d) { return xScale(d.count) + (this.getBBox().width / 3); })
        .attr("y", function(d) { return yScale(d.hour) + yScale.bandwidth() / 2 + (this.getBBox().height / 3); });

    // Update bar lengths
    container.select("g").selectAll(".bar")
        .attr("width", function(d) { return xScale(d.count); })
        .attr("y", function(d) { return yScale(d.hour); })
        .attr("height", yScale.bandwidth());
}
