$(document).ready(function() {

    // check password and confirmpassword.
    $(".pass_match").addClass("hidden");
    $("#u_pass2").change(function() {
        if ($("#u_pass1").val() != $("#u_pass2").val()) {
            $(".pass_match").removeClass("hidden");
            event.preventDefault();
            return false;
        } else {
            $(".pass_match").addClass("hidden");
            return true;
        }
    });

    //Email validation
    $(".email_valid").addClass("hidden");
    $("#u_email").change(function() {
        var filter = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
        if (!filter.test($("#u_email").val())) {
            $(".email_valid").removeClass("hidden");
            return false;
        } else {
            $(".email_valid").addClass("hidden");
            return true;
        }
    });

    openerp.jsonRpc("/get_country", 'call', {}).then(function(data) {
        country_list = data;
        var select = $('#country_id');
        $('option', select).remove();
        var option = new Option('Country', '');
        select.append($(option));
        $(option).attr("disabled", "disabled");
        $(option).attr("selected", "selected");
        $.each(data, function(key, value) {
            option = new Option(value[1], value[0]);
            select.append($(option));
        });
    });

    openerp.jsonRpc("/get_state", 'call', {}).then(function(data) {
        state_list = data;
        var select = $('#state_id');
        $('option', select).remove();
        var option = new Option('state', '');
        select.append($(option));
        $(option).attr("disabled", "disabled");
        $(option).attr("selected", "selected");
        $.each(data, function(key, value) {
            option = new Option(value[1], value[0]);
            select.append($(option));
        });
    });

});