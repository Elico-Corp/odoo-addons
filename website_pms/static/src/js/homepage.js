$(document).ready(function($) {
    $('.counter').counterUp({
        delay: 10,
        time: 1000
    });
});

$(window).load(function() {

    var wi = $(window).width();
    if (wi <= 480){
        $("div").removeClass("form-login");
        $("div").removeClass("col-md-8");
        $("div").removeClass("col-md-offset-2");
        $("div").removeClass("line_set");
    }
    if (wi <= 768){
        $("div").removeClass("line_set");
    }
    //popup banner when homepage load
    /*	$('#popmodal').modal('show');*/

    //set price on the slider dynamically
    openerp.jsonRpc("/min_max_price", 'call', {}).then(function(data) {
        $("#slider_range").slider({
            range: true,
            animate: true,
            step: 500,
            min: data['min_value'],
            max: data['max_value'],
            heterogeneity: ['50/50000'],
            format: {
                format: '##.0',
                locale: 'de'
            },
            dimension: '',
            scale: [0, '|', 50, '|', '100', '|', 250, '|', 500],
            values: [data['min_value'], data['max_value']],
            slide: function(event, ui) {
                $("#amount").val("$" + ui.values[0] + " - $" + ui.values[1]);
                $('#min_property_range_id').val(ui.values[0]);
                $('#max_property_range_id').val(ui.values[1]);
            }
        });
        $("#amount").val("$" + $("#slider_range").slider("values", 0) + " - $" + $("#slider_range").slider("values", 1));
        var $amount = $("#amount").val();
        $('#slider_range a').first().html('<label><span class="glyphicon glyphicon-chevron-left"></span></label>');
        $('#slider_range a').first().next().html('<label><span class="glyphicon glyphicon-chevron-right"></span></label>');
    });

    // bedroom slide js
    $("#bead_slider_range").slider({
        range: true,
        animate: true,
        step: 1,
        min: 1,
        max: 5,
        heterogeneity: ['50/50000'],
        format: {
            format: '##.0',
            locale: 'de'
        },
        dimension: '',
        values: [$('#min_bead_range_id').val(), $('#max_bead_range_id').val()],
        slide: function(event, ui) {
            $("#bead_amount").val("" + ui.values[0] + "-" + ui.values[1]);
            $('#min_bead_range_id').val(ui.values[0]);
            $('#max_bead_range_id').val(ui.values[1]);
        }
    });
    $("#bead_amount").val("" + $("#bead_slider_range").slider("values", 0) + " - " + $("#bead_slider_range").slider("values", 1));
    var $bead_amount = $("#bead_amount").val();
    $('#bead_slider_range a').first().html('<label><span class="glyphicon glyphicon-chevron-left"></span></label>');
    $('#bead_slider_range a').first().next().html('<label><span class="glyphicon glyphicon-chevron-right"></span></label>');

    //  bathroom slide js
    $("#bath_slider_range").slider({
        range: true,
        animate: true,
        step: 1,
        min: 1,
        max: 5,
        heterogeneity: ['50/50000'],
        format: {
            format: '##.0',
            locale: 'de'
        },
        dimension: '',
        values: [$('#min_bath_range_id').val(), $('#max_bath_range_id').val()],
        slide: function(event, ui) {
            $("#bath_amount").val("" + ui.values[0] + "-" + ui.values[1]);
            $('#min_bath_range_id').val(ui.values[0]);
            $('#max_bath_range_id').val(ui.values[1]);
        }
    });
    $("#bath_amount").val("" + $("#bath_slider_range").slider("values", 0) + " - " + $("#bath_slider_range").slider("values", 1));
    var $bath_amount = $("#bath_amount").val();
    $('#bath_slider_range a').first().html('<label><span class="glyphicon glyphicon-chevron-left"></span></label>');
    $('#bath_slider_range a').first().next().html('<label><span class="glyphicon glyphicon-chevron-right"></span></label>');

    // Price list slide js
    openerp.jsonRpc("/min_max_price", 'call', {}).then(function(data) {
        $("#price_slider_range").slider({
            range: true,
            animate: true,
            step: 500,
            min: data['min_value'],
            max: data['max_value'],
            heterogeneity: ['50/50000'],
            format: {
                format: '##.0',
                locale: 'de'
            },
            dimension: '',
            values: [$('#min_price_range_id').val(), $('#max_price_range_id').val()],
            slide: function(event, ui) {
                $("#price_slider").val("$" + ui.values[0] + "- $" + ui.values[1]);
                $('#min_price_range_id').val(ui.values[0]);
                $('#max_price_range_id').val(ui.values[1]);
            }
        });
        $("#price_slider").val("$" + $("#price_slider_range").slider("values", 0) + " - $" + $("#price_slider_range").slider("values", 1));
        var $price_slider = $("#price_slider").val();
        $('#price_slider_range a').first().html('<label><span class="glyphicon glyphicon-chevron-left"></span></label>');
        $('#price_slider_range a').first().next().html('<label><span class="glyphicon glyphicon-chevron-right"></span></label>');
    });

});