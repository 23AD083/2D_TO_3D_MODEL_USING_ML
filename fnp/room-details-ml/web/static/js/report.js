document.addEventListener("DOMContentLoaded", function() {
    const reportContainer = document.getElementById("report-container");

    // Function to fetch and display room details
    function fetchRoomDetails() {
        fetch('/api/room-details')
            .then(response => response.json())
            .then(data => {
                displayRoomDetails(data);
            })
            .catch(error => console.error('Error fetching room details:', error));
    }

    // Function to display room details in the report
    function displayRoomDetails(data) {
        const roomDetails = `
            <h2>Room Details</h2>
            <p>Number of Days: ${data.days}</p>
            <p>Area: ${data.area} sq. ft.</p>
            <p>Walls: ${data.walls}</p>
        `;
        reportContainer.innerHTML += roomDetails;
        createBlueprint(data.blueprint);
        createVisualizations(data.visualizations);
    }

    // Function to create a blueprint visualization
    function createBlueprint(blueprint) {
        const blueprintContainer = document.createElement('div');
        blueprintContainer.innerHTML = `<h3>Blueprint</h3><img src="${blueprint}" alt="Blueprint">`;
        reportContainer.appendChild(blueprintContainer);
    }

    // Function to create visualizations
    function createVisualizations(visualizations) {
        visualizations.forEach(visualization => {
            const img = document.createElement('img');
            img.src = visualization;
            img.alt = "Visualization";
            reportContainer.appendChild(img);
        });
    }

    // Initial fetch of room details
    fetchRoomDetails();
});