
$(function(){
    $('.chkbox').load(function(){
        search_types(map.getCenter());
    });

});

var map;
var infowindow;
var markersArray = [];
var pyrmont = new google.maps.LatLng(20.268455824834792, 85.84099235520011);
var marker;
var geocoder = new google.maps.Geocoder();
var infowindow = new google.maps.InfoWindow();
// var waypoints = [];
function initialize() {
    map = new google.maps.Map(document.getElementById('MAP'), {
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        center: pyrmont,
        zoom: 14
    });
    infowindow = new google.maps.InfoWindow();
    //document.getElementById('directionsPanel').innerHTML='';
    search_types();
   }

function createMarker(place,icon) {

    var placeLoc = place.geometry.location;
    var marker = new google.maps.Marker({
        map: map,
        position: place.geometry.location,
        icon: icon,
        visible:true

    });

    markersArray.push(marker);
    google.maps.event.addListener(marker, 'hover', function() {
        infowindow.setContent("<b>Name:</b>"+place.name+"<br><b>Address:</b>"+place.vicinity+"<br><b>Reference:</b>"+place.reference+"<br><b>Rating:</b>"+place.rating+"<br><b>Id:</b>"+place.id);
        infowindow.open(map, this);
    });

}
var source="";
var dest='';

function search_types(latLng){
    clearOverlays();

    if(!latLng){
        var latLng = pyrmont;
    }
    var type = 'atm';
    var icon = "/website_pms/static/images/"+type+".png";


    var request = {
        location: latLng,
        radius: 2000,
        types: [type] //e.g. school, restaurant,bank,bar,city_hall,gym,night_club,park,zoo
    };

    var service = new google.maps.places.PlacesService(map);
    service.search(request, function(results, status) {
        map.setZoom(14);
        if (status == google.maps.places.PlacesServiceStatus.OK) {
            for (var i = 0; i < results.length; i++) {
                results[i].html_attributions='';
                createMarker(results[i],icon);
            }
        }
    });

    var type2= 'school';
    var icon2 = "/website_pms/static/images/"+type2+".png";


    var request2 = {
        location: latLng,
        radius: 2000,
        types: [type2] //e.g. school, restaurant,bank,bar,city_hall,gym,night_club,park,zoo
    };
    service.search(request2, function(results, status) {
        map.setZoom(14);
        if (status == google.maps.places.PlacesServiceStatus.OK) {
            for (var i = 0; i < results.length; i++) {
                results[i].html_attributions='';
                createMarker(results[i],icon2);
            }
        }
    });


    var type3 = 'gym';
    var icon3 = "/website_pms/static/images/"+type3+".png";


    var request3 = {
        location: latLng,
        radius: 2000,
        types: [type3] //e.g. school, restaurant,bank,bar,city_hall,gym,night_club,park,zoo
    };
    service.search(request3, function(results, status) {
        map.setZoom(14);
        map.setZoom(14);
        if (status == google.maps.places.PlacesServiceStatus.OK) {
            for (var i = 0; i < results.length; i++) {
                results[i].html_attributions='';
                createMarker(results[i],icon3);
            }
        }
    });

    var type4 = 'bank';
    var icon4 = "/website_pms/static/images/"+type4+".png";


    var request4 = {
        location: latLng,
        radius: 2000,
        types: [type4] //e.g. school, restaurant,bank,bar,city_hall,gym,night_club,park,zoo
    };
    service.search(request4, function(results, status) {
        map.setZoom(14);
        if (status == google.maps.places.PlacesServiceStatus.OK) {
            for (var i = 0; i < results.length; i++) {
                results[i].html_attributions='';
                createMarker(results[i],icon4);
            }
        }
    });

    var type5 = 'park';
    var icon5 = "/website_pms/static/images/"+type5+".png";


    var request5 = {
        location: latLng,
        radius: 2000,
        types: [type5] //e.g. school, restaurant,bank,bar,city_hall,gym,night_club,park,zoo
    };
    service.search(request5, function(results, status) {
        map.setZoom(14);
        if (status == google.maps.places.PlacesServiceStatus.OK) {
            for (var i = 0; i < results.length; i++) {
                results[i].html_attributions='';
                createMarker(results[i],icon5);
            }
        }
    });

    var type6 = 'spa';
    var icon6 = "/website_pms/static/images/"+type6+".png";


    var request6 = {
        location: latLng,
        radius: 2000,
        types: [type6] //e.g. school, restaurant,bank,bar,city_hall,gym,night_club,park,zoo
    };
    service.search(request6, function(results, status) {
        map.setZoom(14);
        if (status == google.maps.places.PlacesServiceStatus.OK) {
            for (var i = 0; i < results.length; i++) {
                results[i].html_attributions='';
                createMarker(results[i],icon6);
            }
        }
    });


    var type7 = 'bus_station';
    var icon7 = "/website_pms/static/images/"+type7+".png";


    var request7 = {
        location: latLng,
        radius: 2000,
        types: [type7] //e.g. school, restaurant,bank,bar,city_hall,gym,night_club,park,zoo
    };
    service.search(request7, function(results, status) {
        map.setZoom(14);
        if (status == google.maps.places.PlacesServiceStatus.OK) {
            for (var i = 0; i < results.length; i++) {
                results[i].html_attributions='';
                createMarker(results[i],icon7);
            }
        }
    });


    var type8 = 'bar';
    var icon8 = "/website_pms/static/images/"+type8+".png";


    var request8 = {
        location: latLng,
        radius: 2000,
        types: [type8] //e.g. school, restaurant,bank,bar,city_hall,gym,night_club,park,zoo
    };
    service.search(request8, function(results, status) {
        map.setZoom(14);
        if (status == google.maps.places.PlacesServiceStatus.OK) {
            for (var i = 0; i < results.length; i++) {
                results[i].html_attributions='';
                createMarker(results[i],icon8);
            }
        }
    });

    var type9 = 'hospital';
    var icon9 = "/website_pms/static/images/"+type9+".png";


    var request9 = {
        location: latLng,
        radius: 2000,
        types: [type9] //e.g. school, restaurant,bank,bar,city_hall,gym,night_club,park,zoo
    };
    service.search(request9, function(results, status) {
        map.setZoom(14);
        if (status == google.maps.places.PlacesServiceStatus.OK) {
            for (var i = 0; i < results.length; i++) {
                results[i].html_attributions='';
                createMarker(results[i],icon9);
            }
        }
    });

    var type10 = 'movie_theater';
    var icon10 = "/website_pms/static/images/"+type10+".png";


    var request10 = {
        location: latLng,
        radius: 2000,
        types: [type10] //e.g. school, restaurant,bank,bar,city_hall,gym,night_club,park,zoo
    };
    service.search(request10, function(results, status) {
        map.setZoom(14);
        if (status == google.maps.places.PlacesServiceStatus.OK) {
            for (var i = 0; i < results.length; i++) {
                results[i].html_attributions='';
                createMarker(results[i],icon10);
            }
        }
    });


    var type11 = 'night_club'
    var icon11 = "/website_pms/static/images/"+type11+".png";


    var request11 = {
        location: latLng,
        radius: 2000,
        types: [type11] //e.g. school, restaurant,bank,bar,city_hall,gym,night_club,park,zoo
    };
    service.search(request11, function(results, status) {
        map.setZoom(14);
        if (status == google.maps.places.PlacesServiceStatus.OK) {
            for (var i = 0; i < results.length; i++) {
                results[i].html_attributions='';
                createMarker(results[i],icon11);
            }
        }
    });

    var type12 = 'zoo'
    var icon12 = "/website_pms/static/images/"+type12+".png";


    var request12 = {
        location: latLng,
        radius: 2000,
        types: [type12] //e.g. school, restaurant,bank,bar,city_hall,gym,night_club,park,zoo
    };
    service.search(request12, function(results, status) {
        map.setZoom(14);
        if (status == google.maps.places.PlacesServiceStatus.OK) {
            for (var i = 0; i < results.length; i++) {
                results[i].html_attributions='';
                createMarker(results[i],icon12);
            }
        }
    });

    var type13 = 'gas_station'
    var icon13 = "/website_pms/static/images/"+'fuel'+".png";


    var request13 = {
        location: latLng,
        radius: 2000,
        types: [type13] //e.g. school, restaurant,bank,bar,city_hall,gym,night_club,park,zoo
    };
    service.search(request13, function(results, status) {
        map.setZoom(14);
        if (status == google.maps.places.PlacesServiceStatus.OK) {
            for (var i = 0; i < results.length; i++) {
                results[i].html_attributions='';
                createMarker(results[i],icon13);
            }
        }
    });
 }


// Deletes all markers in the array by removing references to them
function clearOverlays() {
    if (markersArray) {
        for (i in markersArray) {
            markersArray[i].setVisible(false)
        }
        //markersArray.length = 0;
    }
}
google.maps.event.addDomListener(window, 'load', initialize);

function clearMarkers(){
    $('#show_btn').show();
    $('#hide_btn').hide();
    clearOverlays()
}
function showMarkers(){
    $('#show_btn').hide();
    $('#hide_btn').show();
    if (markersArray) {
        for (i in markersArray) {
            markersArray[i].setVisible(true)
        }

    }
}

function showMap(){

    var imageUrl = 'http://chart.apis.google.com/chart?cht=mm&chs=24x32&chco=FFFFFF,008CFF,000000&ext=.png';
    var markerImage = new google.maps.MarkerImage(imageUrl,new google.maps.Size(24, 32));
    var input_addr=$("#pro_street").html() + ' ' + $("#pro_street2").html() + ' ' + $("#pro_city").html() + ' ' + $("#pro_state").html() + ' ' + $("#pro_country").html() + ' ' + $("#pro_zip").html();
    geocoder.geocode({address: input_addr}, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            var latitude = results[0].geometry.location.lat();
            var longitude = results[0].geometry.location.lng();
            var latlng = new google.maps.LatLng(latitude, longitude);
            if (results[0]) {
                map.setZoom(14);
                map.setCenter(latlng);
                marker = new google.maps.Marker({
                    position: latlng,
                    map: map,
                    icon: markerImage,
                    draggable: true

                });
                $('#btn').hide();
                $('#latitude,#longitude').show();
                $('#address').val(results[0].formatted_address);
                $('#latitude').val(marker.getPosition().lat());
                $('#longitude').val(marker.getPosition().lng());
                infowindow.setContent(results[0].formatted_address);
                infowindow.open(map, marker);
                search_types(marker.getPosition());
                google.maps.event.addListener(marker, 'click', function() {
                    infowindow.open(map,marker);

                });


                google.maps.event.addListener(marker, 'dragend', function() {

                    geocoder.geocode({'latLng': marker.getPosition()}, function(results, status) {
                        if (status == google.maps.GeocoderStatus.OK) {
                            if (results[0]) {
                                $('#btn').hide();
                                $('#latitude,#longitude').show();
                                $('#address').val(results[0].formatted_address);
                                $('#latitude').val(marker.getPosition().lat());
                                $('#longitude').val(marker.getPosition().lng());
                            }

                            infowindow.setContent(results[0].formatted_address);
                            var centralLatLng = marker.getPosition();
                            search_types(centralLatLng);
                            infowindow.open(map, marker);
                        }
                    });
                });


            } else {
                alert("No results found");
            }
        } else {
            alert("Geocoder failed due to: " + status);
        }
    });

}

