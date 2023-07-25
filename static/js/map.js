
function zoomed() {
    svg.selectAll('path').attr('transform', d3.event.transform);
    svg.selectAll('circle').attr('transform', d3.event.transform);
}
let width = 960,
    height = 500;

let svg = d3.select("body").append("svg")
.attr("width", width)
.attr("height", height);

// Define the zoom behavior
let zoom = d3.zoom()
    .scaleExtent([1, 10])
    .on("zoom", zoomed);

// Apply the zoom behavior to the svg
svg.call(zoom);

let projection = d3.geoNaturalEarth1();

let path = d3.geoPath()
.projection(projection);

console.log("Starting to draw world map...");

d3.json('/static/world_map.json')
.then(function(world) {
    console.log("Drawing world map...");
    svg.append("path")
    .datum(world)
    .attr("d", path)
    .style("fill", "#efefef")
    .style("stroke", "#333");
});

console.log("Starting to load GeoJSON data...");

// Loading and drawing the points from your GeoJSON data
d3.json("/get_geojson_data")
.then(function(geojson) {
    console.log("Processing GeoJSON data...");

    // Create tooltip
    var tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);

    svg.selectAll("circle")
        .data(geojson.features)
        .enter()
        .append("circle")
        .attr("r", 5)
        .attr("fill", "rgba(217, 91, 67, 0.8)")  // A nice red color
        .attr("stroke", "#fff")  // White stroke
        .attr("stroke-width", 1.5)  // Stroke width
        .attr("transform", function(d) {
            var coords = d.geometry.coordinates;
            var lon = coords[0];
            var lat = coords[1];
            if (lon === null || lat === null) {
                return;
            }
            var projected = projection([lon, lat]);
            return "translate(" + projected + ")";
        })
        .on("mouseover", function(d) {  // when mouse enters div
            tooltip.transition()
                .duration(100)  // how long u want to wait before tooltip appears
                .style("opacity", 1);  // used to set opacity to fully visible
            tooltip.html(d.properties.headline)
                .style("left", (d3.event.pageX + 10) + "px")
                .style("top", (d3.event.pageY - 10) + "px");
        })
        .on("mouseout", function(d) {  // when mouse leaves div
            tooltip.transition()
                .duration(500) // how long u want to wait before tooltip disappears
                .style("opacity", 0);
        })
        .transition()  // Transition effect
        .duration(200)
        .ease(d3.easeCircleIn);
})
.catch(function(error) {
    console.log("A problem occurred while loading GeoJSON data. Error: ", error);
});

console.log("End of script.");