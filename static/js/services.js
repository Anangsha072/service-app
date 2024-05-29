const locationCoordinates = {
    "Delhi": { latitude: 28.7041, longitude: 77.1025 },
    "Mumbai": { latitude: 19.0760, longitude: 72.8777 },
    "Bangalore": { latitude: 12.9716, longitude: 77.5946 },
    "Kolkata": { latitude: 22.5726, longitude: 88.3639 },
    "Chennai": { latitude: 13.0827, longitude: 80.2707 },
    "Hyderabad": { latitude: 17.3850, longitude: 78.4867 },
    "Pune": { latitude: 18.5204, longitude: 73.8567 },
    "Ahmedabad": { latitude: 23.0225, longitude: 72.5714 },
    "Jaipur": { latitude: 26.9124, longitude: 75.7873 },
    "Lucknow": { latitude: 26.8467, longitude: 80.9462 }
};

function getCurrentLocation(serviceType) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            console.log(`Latitude: ${latitude}, Longitude: ${longitude}`);
            fetchServices(serviceType, latitude, longitude);
        }, showError);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

function useManualLocation(serviceType) {
    const location = document.getElementById("location").value;
    const coordinates = locationCoordinates[location];
    if (coordinates) {
        const latitude = coordinates.latitude;
        const longitude = coordinates.longitude;
        console.log(`Latitude: ${latitude}, Longitude: ${longitude}`);
        fetchServices(serviceType, latitude, longitude);
    } else {
        alert("Invalid location.");
    }
}

function fetchServices(serviceType, latitude, longitude) {
    $.ajax({
        url: "/fetch_services",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({ serviceType, latitude, longitude }),
        success: function(data) {
            displayServices(data);
        },
        error: function(error) {
            console.error("Error fetching services:", error);
        }
    });
}

function displayServices(services) {
    const serviceList = document.getElementById("serviceList");
    serviceList.innerHTML = "";
    services.forEach(service => {
        const listItem = document.createElement("li");
        listItem.textContent = `${service.name} - (${service.latitude}, ${service.longitude})`;
        serviceList.appendChild(listItem);
    });
}

function showError(error) {
    switch(error.code) {
        case error.PERMISSION_DENIED:
            alert("User denied the request for Geolocation.");
            break;
        case error.POSITION_UNAVAILABLE:
            alert("Location information is unavailable.");
            break;
        case error.TIMEOUT:
            alert("The request to get user location timed out.");
            break;
        case error.UNKNOWN_ERROR:
            alert("An unknown error occurred.");
            break;
    }
}

document.getElementById("login-form").addEventListener("submit", function(event) {
    event.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    if (username === "user" && password === "password") {
        document.getElementById("login-container").style.display = "none";
        document.getElementById("service-container").style.display = "block";
    } else {
        alert("Invalid login credentials");
    }
});
