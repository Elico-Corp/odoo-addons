//Method to change Main property image when click on thumbnail image
$(".image_thumb").click(function() {
    $('#ex1').children().children().attr("src", this.src);
    $('#ex1').children().children().attr("id", "image2"); // Give Id to image
});

$(document).ready(function() {

    $(".fav_img").change(function() {
        var toggle = $(this).prop('checked');
        var propert_id = $(this).parent();
        openerp.jsonRpc("/change_fav_property", 'call', {
            'fav_checked': $(this).prop('checked'),
            'fav_property': $(this).attr('data')
        }).then(function() {});
    });

    $(".fav_img").change(function() {
        var toggle = $(this).prop('checked');
        var propert_id = $(this).parent();
        openerp.jsonRpc("/change_fav_property", 'call', {
            'fav_checked': $(this).prop('checked'),
            'fav_property': $(this).attr('data')
        }).then(function(data) {
            //$("#no_of_property").text(data['fav_assets']);
            location.reload();
        });
    });

    /* form submit on sale & rent button click  */
    $("#sale_btn_id").click(function() {
        var input_tag = '<input type="hidden" name="type_of_property" value="sale"/>';
        $('#search_form').append(input_tag).submit();
    });

    $("#rent_btn_id").click(function() {
        var input_tag = '<input type="hidden" name="type_of_property" value="rent"/>';
        $('#search_form').append(input_tag).submit();
    });

    $("#sale_btn_search_id").click(function() {
        var input_tag = '<input type="hidden" name="type_of_property" value="sale"/>';
        $('#property_list_display').append(input_tag).submit();
    });

    $("#rent_btn_search_id").click(function() {
        var input_tag = '<input type="hidden" name="type_of_property" value="rent"/>';
        $('#property_list_display').append(input_tag).submit();
    });

    /* filter change event call */
    $('.dropdown_filter_change').change(function() {
        $('#property_list_display').submit();
    });

    $('.search_filter_change').click(function() {
        $('#property_list_display').submit();
    });

    $('.btn_new_search').click(function() {
        $('#property_btns').removeClass("hidden");
        var div = document.getElementById('property_filter');
        if (div.style.display !== 'none') {
            div.style.display = 'none';
        } else {
            div.style.display = 'block';
            $('#property_btns').addClass("hidden");
        }
    });

    /* show/hide in mobile screen */
    $('.btn_property_search').click(function() {
        $('.property_search').removeClass("hidden-xs");
        $('.new_search').addClass("hidden-xs");
    });
    $('.btn_new_search').click(function() {
        $('.new_search').removeClass("hidden-xs");
        $('.new_search').removeClass("hidden");
        $('.property_search').addClass("hidden-xs");
    });
    $('.btn_form_search').click(function() {
        $('.form_search').removeClass("hidden-xs");
    });
    $('.btn_new_show').click(function() {
        $('.property_search').removeClass("hidden-xs");
        $('.new_search').removeClass("hidden-xs");
        $('.new_search').removeClass("hidden");
        $('.new_search').removeClass("collapse");
    });

    $('.btn_new_show').click(function() {
        $('#property_btns').removeClass("hidden");
        var div = document.getElementById('property_filter');
        if (div.style.display !== 'none') {
            div.style.display = 'none';
        } else {
            div.style.display = 'block';
            $('#property_btns').addClass("hidden");
        }
    });

    $('#btn_show_form').click(function() {
        $('#sidebar').each(function() {});
    });

    $('.btn_form_search').click(function() {
        $('.form_lead').addClass("collapse");
        $('.form_search').removeClass("hidden-xs");
        $('.form_lead').removeClass("fixed");
        $('.form_lead').removeClass("sidebar_view");
    });

    $(".btn_grid").click(function() {
        $(".grid_display").removeClass("hide");
        $(".grid").addClass("active");
        $(".list").removeClass("active");
        $(".grid_display").show();
        $(".list_display").hide();
    });
    $(".btn_list").click(function() {
        $(".grid").removeClass("active");
        $(".list").addClass("active");
        $(".list_display").show();
        $(".grid_display").hide();
    });

    //  modal call
    $(".thank_you").addClass("hidden");
    $('.contact_agent').click(function() {
        var property_id = $(this).parent().find('.property_detail').val();
        openerp.jsonRpc("/agent_modal", 'call', {
            'property_id': property_id
        }).then(function(modal) {
            x = property_id;
            var $modal = $(modal);
            $form = $('#list_display');
            $modal.appendTo($form).modal().on('hidden.bs.modal', function() {
                $(this).remove();
            });
            $('#asset_modal_id').val(x);
            $modal.find('#send_agent_modal_id').click(function() {
                vals = {
                    'firstname': $("#inputFirstName").val(),
                    'surname': $("#inputSurname").val(),
                    'email': $("#inputEmail").val(),
                    'tel': $("#inputTel").val(),
                    'telType': $("#inputTelType").val(),
                    'telTime': $("#inputTelTime").val(),
                    'msg': $("#inputMsg").val(),
                    'asset': $("#asset_modal_id").val(),
                }; //lead create
                console.log("val---", vals);
                openerp.jsonRpc("/create_lead", 'call', vals).then(function(data) {});
                console.log("lead ===");
                $(".contact_agent").each(function() {
                    if (this.id == x) {
                        $(this).hide();
                        $(this).parent().find(".thank_you").removeClass("hidden");
                    };
                });
            });
        });
    });

    $('.contact_demand').click(function() {
        openerp.jsonRpc("/demand_modal", 'call', {
        }).then(function(modal) {
            var $modal = $(modal);
            $form = $('#list_display');
            $modal.appendTo($form).modal().on('hidden.bs.modal', function() {
                $(this).remove();
            });
//            $('#asset_modal_id').val(x);
            $modal.find('#send_agent_modal_id').click(function() {
                vals = {
                    'firstname': $("#inputFirstName").val(),
                    'surname': $("#inputSurname").val(),
                    'email': $("#inputEmail").val(),
                    'tel': $("#inputTel").val(),
                    'telType': $("#inputTelType").val(),
                    'telTime': $("#inputTelTime").val(),
                    'msg': $("#inputMsg").val(),
                    'street':$("#inputStreet").val(),
                    'street2':$("#inputstreet2").val(),
                    'state':$("#inputState").val(),
                    'country':$("#inputCountry").val(),
                    'city':$("#inputCity").val(),
                    'zip':$("#inputZip").val(),
                    'furnished':$("#inputFurnished").val(),
                    'min_price':$("#min_price_range_id").val(),
                    'max_price':$("#max_price_range_id").val(),
                    'facing':$("#inputFacing").val(),
                    'min_bedroom':$("#min_bead_range_id").val(),
                    'max_bedroom':$("#max_bead_range_id").val(),
                    'min_bathroom':$("#min_bath_range_id").val(),
                    'max_bathroom':$("#max_bath_range_id").val(),
                    'type_id':$("#inputType").val(),
                }; //lead create
                openerp.jsonRpc("/create_lead_demand", 'call', vals).then(function(data) {});
                $(".contact_agent").each(function() {
                    if (this.id == x) {
                        $(this).hide();
                        $(this).parent().find(".thank_you").removeClass("hidden");
                    };
                });
            });
        });
    });

    // modal call from fourites
    $(".fav_thank_you").addClass("hidden");
    $('.fav_contact_agent').click(function() {
        var property_id = $(this).parent().find('.fav_property_detail').val();
        openerp.jsonRpc("/fav_agent_modal", 'call', {
            'property_id': property_id
        }).then(function(modal) {
            x = property_id;
            var $modal = $(modal);
            $form = $('#fav_list_display_id');
            $modal.appendTo($form).modal().on('hidden.bs.modal', function() {
                $(this).remove();
            });
            $('#fav_asset_modal_id').val(x);
            $modal.find('#fav_send_agent_modal_id').click(function() {
                vals = {
                    'firstname': $("#inputFirstName").val(),
                    'surname': $("#inputSurname").val(),
                    'email': $("#inputEmail").val(),
                    'tel': $("#inputTel").val(),
                    'telType': $("#inputTelType").val(),
                    'telTime': $("#inputTelTime").val(),
                    'msg': $("#inputMsg").val(),
                    'asset': $("#fav_asset_modal_id").val(),
                }; //lead create
                openerp.jsonRpc("/create_lead", 'call', vals).then(function(data) {});
                $(".fav_contact_agent").each(function() {
                    if (this.id == x) {
                        $(this).hide();
                        $(this).parent().find(".fav_thank_you").removeClass("hidden");
                    };
                });
            });
        });
    });

    //lead create
    $(".thank_you_msg").addClass("hidden");
    $('#send_agent_id').click(function() {
        vals = {
            'firstname': $("#inputFirstName").val(),
            'surname': $("#inputSurname").val(),
            'email': $("#inputEmail").val(),
            'tel': $("#inputTel").val(),
            'telType': $("#inputTelType").val(),
            'telTime': $("#inputTelTime").val(),
            'msg': $("#inputMsg").val(),
            'asset': $("#asset_id").val(),
            'asset_state': $("#asset_state_id").val(),
        };
        openerp.jsonRpc("/create_lead", 'call', vals).then(function(data) {});
        $(".thank_you_msg").removeClass('hidden');
        $(".form_lead").addClass("hidden");
    });
});

    // Scroll Top hide/show
    $(function() {
        $(document).on('scroll', function() {
            if ($(window).scrollTop() > 100) {
                $('.scroll-top-wrapper').addClass('show');
            } else {
                $('.scroll-top-wrapper').removeClass('show');
            }
        });
    });
    // Scroll Top manage
    $(function() {
        $(document).on('scroll', function() {
            if ($(window).scrollTop() > 100) {
                $('.scroll-top-wrapper').addClass('show');
            } else {
                $('.scroll-top-wrapper').removeClass('show');
            }
        });
        $('.scroll-top-wrapper').on('click', scrollToTop);
    });
    // Scroll Top Move 
    function scrollToTop() {
        verticalOffset = typeof(verticalOffset) != 'undefined' ? verticalOffset : 0;
        element = $('body');
        offset = element.offset();
        offsetTop = offset.top;
        $('html, body').animate({
            scrollTop: offsetTop
        }, 500, 'linear');
    }
