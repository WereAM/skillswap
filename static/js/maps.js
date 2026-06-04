let map, marker, autocomplete;

function initMap() {
    // Nairobi as default centre
    const defaultPos = { lat: -1.286, lng: 36.817 };

    map = new google.maps.Map(document.getElementById('map'), {
        center: defaultPos,
        zoom: 13,
        styles: [
            { elementType: 'geometry',
                stylers: [{ color: '#f5f5f0' }]
            },
            { featureType: 'water',
                stylers: [{ color: '#c9d9d9' }]
            },
            { featureType: 'road',
                elementType: 'geometry',
                stylers: [{ color: '#ffffff' }]
            },
        ],
    });

    // autocomplete on location search input
    const input = document.getElementById('location-search');
    autocomplete = new google.maps.places.Autocomplete(input);
    autocomplete.bindTo('bounds', map);

    autocomplete.addListener('place_changed', function() {
        const place = autocomplete.getPlace();
        if (!place.geometry) return;

        map.setCenter(place.geometry.location);
        map.setZoom(15);
        placeMarker(place.geometry.location);

        // store the latitudes/longitudes in hidden fields
        document.querySelector('[name="location_latitude"]').value = place.geometry.location.lat();
        document.querySelector('[name="location_longitude"]').value = place.geometry.location.lng();
    });

    // allow clicking on map to place marker
    map.addListener('click', function(e) {
        placeMarker(e.latLng);
        document.querySelector('[name="location_latitude"]').value = e.latLng.lat();
        document.querySelector('[name="location_longitude"]').value = e.latLng.lng();

        // reverse geocode to get address
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({ location: e.latLng }, function(results, status) {
            if (status === 'OK' && results[0]) {
                document.getElementById('location-search').value = results[0].formatted_address;
            }
        });
    });
}

function placeMarker(position) {
    if (marker) marker.setMap(null);
    marker = new google.maps.Marker({
        position: position,
        map: map,
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 10,
            fillColor: '#1D5D5D',
            fillOpacity: 1,
            strokeColor: '#ffffff',
            strokeWeight: 2,
        }
    });
}