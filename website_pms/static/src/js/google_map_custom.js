$(document).ready(function() {

    location_address = $("#pro_street").html() + ' ' + $("#pro_street2").html() + ' ' + $("#pro_city").html() + ' ' + $("#pro_state").html() + ' ' + $("#pro_country").html() + ' ' + $("#pro_zip").html();
    initialize(23.195648, 72.619236);
    var map;
    var infowindow;

    /* Get langitude and longitude from adress  */
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({
        'address': location_address
    }, function(results, status) {
        var location = results[0].geometry.location;
        var pyrmont = {
            lat: location.lat(),
            lng: location.lng()
        }
        initialize(location.lat(), location.lng());
    });

    /* Call intialize methods */
    function initialize(lat, lang) {
        var pyrmont = new google.maps.LatLng(lat, lang);
        map = new google.maps.Map(document.getElementById('map'), {
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            center: pyrmont,
            zoom: 16
        });
        var request = {
            location: pyrmont,
            radius: 500,
            types: ['store']
        };
        infowindow = new google.maps.InfoWindow();
        var service = new google.maps.places.PlacesService(map);
        service.search(request, callback);
    }
    /* Call and serch near about place */
    function callback(results, status) {
        if (status == google.maps.places.PlacesServiceStatus.OK) {
            for (var i = 0; i < results.length; i++) {
                createMarker(results[i]);
            }
        }
    }

    /* Mark all near about place */
    function createMarker(place) {
        var placeLoc = place.geometry.location;

        var marker = new google.maps.Marker({
            map: map,
            position: place.geometry.location,
            icon: {
              url: '/website_pms/static/src/img/icon.png',
              size: new google.maps.Size(40, 40),
              origin: new google.maps.Point(0, 0),
              anchor: new google.maps.Point(0, 0),
             scaledSize: new google.maps.Size(20, 20)
           }
        });
        google.maps.event.addListener(marker, 'click', function() {
            infowindow.setContent(place.name);
            infowindow.open(map, this);
        });
    }
});