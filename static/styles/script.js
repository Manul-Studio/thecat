let map, infoWindow;
let marker;
let geocoder;
let responseDiv;
let response;

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 51.107546, lng: 17.0382034 },
    zoom: 6,
  });
  infoWindow = new google.maps.InfoWindow();

  const locationButton = document.createElement("button");

  locationButton.textContent = "Pan to Current Location";
  locationButton.classList.add("custom-map-control-button");
  map.controls[google.maps.ControlPosition.TOP_CENTER].push(locationButton);
  locationButton.addEventListener("click", () => {
    // Try HTML5 geolocation.
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const pos = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };

          infoWindow.setPosition(pos);
          infoWindow.setContent("Location found.");
          infoWindow.open(map);
          map.setCenter(pos);
        },
        () => {
          handleLocationError(true, infoWindow, map.getCenter());
        }
      );
    } else {
      // Browser doesn't support Geolocation
      handleLocationError(false, infoWindow, map.getCenter());
    }
  });
  geocoder = new google.maps.Geocoder();

  const inputText = document.createElement("input");

  inputText.type = "text";
  inputText.placeholder = "Enter a location";

  const submitButton = document.createElement("input");

  submitButton.type = "button";
  submitButton.value = "Search";
  submitButton.classList.add("button", "button-primary");

  const clearButton = document.createElement("input");

  clearButton.type = "button";
  clearButton.value = "Clear";
  clearButton.classList.add("button", "button-secondary");
  response = document.createElement("pre");
  response.id = "response";
  response.innerText = "";
  responseDiv = document.createElement("div");
  responseDiv.id = "response-container";
  responseDiv.appendChild(response);

  const instructionsElement = document.createElement("p");

  map.controls[google.maps.ControlPosition.TOP_LEFT].push(inputText);
  map.controls[google.maps.ControlPosition.TOP_LEFT].push(submitButton);
  map.controls[google.maps.ControlPosition.TOP_LEFT].push(clearButton);
  map.controls[google.maps.ControlPosition.LEFT_TOP].push(instructionsElement);

  marker = new google.maps.Marker({
    map,
  });
  map.addListener("click", (e) => {
    geocode({ location: e.latLng });
  });
  submitButton.addEventListener("click", () => geocode({ address: inputText.value }));
  clearButton.addEventListener("click", clear);
  clear();
  function clear() {
    marker.setMap(null);
    responseDiv.style.display = "none";
  }

  function geocode(request) {
    clear();

    geocoder
      .geocode(request)
      .then((result) => {
        const { results } = result;

        if (results.length > 0) {
          const location = results[0].geometry.location;
          const addressComponents = results[0].address_components;
          const placeId = results[0].place_id;

          // Extract required information
          const city = getAddressComponent(addressComponents, "locality");
          const country = getAddressComponent(addressComponents, "country");
          const zipcode = getAddressComponent(addressComponents, "postal_code");
          const streetName = getAddressComponent(addressComponents, "route");
          const streetNumber = getAddressComponent(addressComponents, "street_number");

          console.log("City:", city);
          console.log("Country:", country);
          console.log("Zip Code:", zipcode);
          console.log("Street Name:", streetName);
          console.log("Street Number:", streetNumber);

          // Display marker for the clicked location
          createMarkerForLocation({
            latitude: location.lat(),
            longitude: location.lng(),
            city: city,
            country: country,
            street_number: streetNumber,
            street_name: streetName,
            address: results[0].formatted_address,
          });

          map.setCenter(location);
          marker.setPosition(location);
          marker.setMap(map);
          responseDiv.style.display = "block";
          response.innerText = JSON.stringify(result, null, 2);

          // Send the location data to the Django server
          const data = {
            latitude: location.lat(),
            longitude: location.lng(),
            city: city,
            country: country,
            zipcode: zipcode,
            place_id: placeId,
            street_number: streetNumber,
            street_name: streetName,
          };
          saveLocationToDatabase(data);
        }

        return results;
      })
      .catch((e) => {
        alert("Geocode was not successful for the following reason: " + e);
      });
  }

  function getAddressComponent(addressComponents, type) {
    for (const component of addressComponents) {
      if (component.types.includes(type)) {
        return component.long_name;
      }
    }
    return null;
  }

  function createMarkerForLocation(location) {
    console.log("Creating marker for location:", location);

    const marker = new google.maps.Marker({
      position: { lat: parseFloat(location.latitude), lng: parseFloat(location.longitude) },
      map: map,
      title: location.address,
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    const addressLinks = document.querySelectorAll('.address-link');

    addressLinks.forEach(function (link) {
      link.addEventListener('click', function (e) {
        e.preventDefault();

        const locationData = {
          latitude: link.dataset.latitude,
          longitude: link.dataset.longitude,
          city: link.dataset.city,
          country: link.dataset.country,
          street_name: link.dataset.streetName,
          street_number: link.dataset.streetNumber,
          address: link.innerText, // Assuming the address is displayed as text in the link
        };

        console.log("Link clicked:", locationData);

        // Assuming you have a geocode function
        geocode({ location: new google.maps.LatLng(locationData.latitude, locationData.longitude) });

        // Create marker for the clicked location
        createMarkerForLocation(locationData);
      });
    });
  });
}
function saveLocationToDatabase(data) {
  // Send a POST request to the Django server to save the location
  fetch("/map/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json", // Update content type to JSON
      "X-CSRFToken": getCookie("csrftoken"), // Include CSRF token for security
    },
    body: JSON.stringify(data), // Use JSON.stringify
  })
    .then((response) => response.json())
    .then((data) => console.log(data))
    .catch((error) => console.error("Error:", error));
}

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
  infoWindow.setPosition(pos);
  infoWindow.setContent(
    browserHasGeolocation
      ? "Error: The Geolocation service failed."
      : "Error: Your browser doesn't support geolocation."
  );
  infoWindow.open(map);
}

window.initMap = initMap;
