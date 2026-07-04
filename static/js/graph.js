// static/js/graph.js
document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById("graph-canvas");
    if (!container) return;

    // Load active structural configurations from Flask API
    fetch("/api/graph-data")
        .then(response => response.json())
        .then(data => {
            const graphData = {
                nodes: new vis.DataSet(data.nodes),
                edges: new vis.DataSet(data.edges)
            };

            const options = {
                nodes: {
                    shape: "dot",
                    font: { size: 14, color: "#ffffff" }
                },
                edges: {
                    width: 2,
                    smooth: { type: "continuous" }
                },
                physics: {
                    stabilization: true,
                    barnesHut: {
                        gravitationalConstant: -12000,
                        springLength: 120,
                        springConstant: 0.04
                    }
                }
            };

            // Initialize Vis.js network instance
            const network = new vis.Network(container, graphData, options);
        })
        .catch(err => console.error("Error loading network graph data:", err));
});