
var width = 600,
    height = 100;
var cellHeight = 20, cellWidth = 20, cellPadding = 10;

var svg = d3.select("#date-chart").append("svg")
    .attr("width", width)
    .attr("height", height);
    
var dummy_data = [0,0,1,1,1,1,1,1,0,1,0,1,1,1,1];

var squares = svg.selectAll('rect')
         .data(dummy_data)
         .enter()
         .append("rect")

var squareattr = squares
        .attr("width", 30)
        .attr("height", 40)
        .attr("x", function(d, i) {
            return 40*i
        })
        .attr("y", 10)
        .style("fill", function(d) {
            if (d == 1) {
                return "5de7e4"
            }
            else {
                return "#BEBCC2"
            }
        });