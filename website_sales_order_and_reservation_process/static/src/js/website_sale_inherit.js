$(document).ready(function () {
    $('.oe_website_sale').each(function () {
        var oe_website_sale = this;

        $(oe_website_sale).on('change', 'input.js_variant_change, select.js_variant_change, ul[data-attribute_value_ids]', function (event) {
            product_ids = [];
            var product_dom = $("ul.js_add_cart_variants[data-attribute_value_ids]").first();
            product_dom.data("attribute_value_ids").forEach(function(entry) {
                product_ids.push(entry[0]);});
            var qty = $(event.target).closest('form').find('input[name="add_qty"]').val();

            openerp.jsonRpc("/shop/check_stock_inventory", 'call', {'product_ids': product_ids,'add_qty': parseInt(qty)})
            .then(function (data) {
                var reserve_dom = $("a.js_reserve");
                var check_dom = $("a.js_check_product");

                if (data){
                    check_dom.removeAttr("disabled");
                    reserve_dom.attr("style","display:none");
                }else {
                    check_dom.attr("disabled","disabled");
                    reserve_dom.removeAttr("style");
                }
                
                return
            });
        });

        $(oe_website_sale).on("change", ".oe_cart input.js_quantity", function (event) {
            var $input = $(this);
            var value = parseInt($input.val(), 10);
            var line_id = parseInt($input.data('line-id'),10);
            var product_id = parseInt($input.data('product-id'),10);
            var product_ids = [product_id];
            if (isNaN(value)) value = 0;

            openerp.jsonRpc("/shop/check_stock_inventory", 'call', {'product_ids': product_ids,'add_qty': value})
            .then(function (data) {
                var inventory_dom = $('.js_inventory[data-line-id='+line_id+']');
                if (data){
                    inventory_dom.attr("style","color:green");
                    inventory_dom.val("Purchase").html("Purchase");
                }else {
                    inventory_dom.attr("style","color:red");
                    inventory_dom.val("Order").html("Order");
                }
                
                return
            }); 
        });
    });
});
