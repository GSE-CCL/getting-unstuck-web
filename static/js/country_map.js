let country_map = (countries_data) => {
    // Scale to container
    let width = document.getElementById("country-map").offsetWidth,
        height = width / 640 * 360;

    let svg = d3.select("#country-map").append("svg")
                                    .attr("width", width)
                                    .attr("height", height);

    // Define the div for the tooltip
    let div = d3.select("body").append("div")
                            .attr("class", "tooltip")
                            .style("opacity", 0);

    let path = d3.geoPath();
    let projection = d3.geoMercator()
        .translate([width / 2, height / 2 + 40])
        .scale(width / 640 * 100);

    queue()
        .defer(d3.json, "http://enjalot.github.io/wwsd/data/world/world-110m.geojson")
        .await(createVisualization);

    function createVisualization(error, topo) {
        if (error) throw error;

        // Draw the map
        svg.append("g").selectAll("path")
            .data(topo.features.filter(d => d.id !== "GRL" && d.id !== "ATA"))
            .enter().append("path")
            .attr("d", d3.geoPath().projection(projection))
            .attr("fill", function (d){
                // Pull data for this country
                d.count = countries_data.get(d.properties["name"]) || 0;

                // Set the color
                if (d.count > 0) {
                    return "#f9d433"; 
                }
                else {
                    return "#bbb";
                }
            })
            .on("mouseover", function(d) {
                if (d.count > 0) {
                    div.transition()
                    .duration(200)
                    .style("opacity", .9);
                div.html(d.properties["name"] +": " +d.count)
                    .style("left", (d3.event.pageX) + "px")
                    .style("top", (d3.event.pageY - 28) + "px");
                } 
            })
            .on("mouseout", function(d) {
                div.transition()
                    .duration(500)
                    .style("opacity", 0);
            });
    }
};

let bar_graph = (dataset, id, margin = {x: 30, y: 30}, barcolor = (d) => { return "#f9d433" }) => {
    // Define the div for the tooltip
    let div = d3.select("body").append("div")
                            .attr("class", "tooltip")
                            .style("opacity", 0);

    // Scale to container
    let width = document.getElementById(id).offsetWidth,
        height = width / 640 * 360;

    let svg = d3.select("#" + id).append("svg")
                                         .attr("width", width)
                                         .attr("height", height);
    
    let xScale = d3.scaleBand().range([0, width - 2 * margin.x]).padding(0.4),
        yScale = d3.scaleLinear().range([height - 2 * margin.y, 0]);

    let g = svg.append("g");

    xScale.domain(dataset.map(function(d) { return d.get("key"); }));
    yScale.domain([0, d3.max(dataset.map(function(d) { return d.get("value"); }))]);

    g.append("g")
        .style("font", ".8rem p22-underground")
        .attr("transform", "translate(" + margin.x + "," + (height - margin.y) + ")")
        .call(d3.axisBottom(xScale));

    g.append("g")
        .style("font", ".8rem p22-underground")
        .attr("transform", "translate(" + margin.x + ", " + (margin.y) + ")")
        .call(d3.axisLeft(yScale));

    g.selectAll(".bar")
        .data(dataset)
        .enter().append("rect")
        .attr("class", "bar")
        .attr("x", function(d) { return xScale(d.get("key")); })
        .attr("y", function(d) { return yScale(d.get("value")); })
        .attr("width", xScale.bandwidth())
        .attr("transform", "translate( " + margin.x + ", " + margin.y + ")")
        .attr("height", function(d) { return height - 2 * margin.y - yScale(d.get("value")); })
        .attr("fill", barcolor)
        .on("mouseover", function(d) {
            if (d.get("value") > 0) {
                div.transition()
                .duration(200)
                .style("opacity", .9);
            div.html(d.get("key") + ": " + d.get("value"))
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
            } 
        })
        .on("mouseout", function(d) {
            div.transition()
                .duration(500)
                .style("opacity", 0);
        });
};
