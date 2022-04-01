odoo.define('products_quick_quotation.QuickQuotationRenderer', function (require) {
    "use strict";

    var AbstractRenderer = require('web.AbstractRenderer');
    var Context = require('web.Context');  
    var core = require('web.core');
    var QWeb = core.qweb;

    var _t = core._t;

    var QuickQuotationRenderer = AbstractRenderer.extend({
        template: 'QuickQuotationView',
        xmlDependencies: ['/products_quick_quotation/static/src/xml/quick_quotation.xml'],
        events: {
            'click a.add_to_cart': 'action_add_to_cart',
            'click button.delete_from_cart': 'action_delete_from_cart',
        },
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.modelName = params.modelName; 
            this.res_partner = state.res_partner; 
            this.cart = [];
        },
        _render: function () {
            var $productArea = this.$el.find('.qq_products_area');
            if ($productArea.length) {
                var $Boxes= $(QWeb.render('QuickQuotationBox', {widget: this}))
                $productArea.html($Boxes);

                for (var $ghost, i = 0; i < 6; i++) {
                    $ghost = $('<div>').addClass('qq_o_kanban_record qq_o_kanban_ghost');
                    $ghost.appendTo($productArea);
                }
            }
            return this._super.apply(this, arguments);
        },
        action_add_to_cart: function(ev){
            var self =  this;
            var product_id = ev.currentTarget.dataset.product_id;
            var product_name = ev.currentTarget.dataset.product_name;

            if (this.cart.includes(product_id)){
                self.displayNotification({ message: _t('Warning: Already added to Select Products Line'), type: 'danger' });
            }
            else{
                var $lineTable = self.$el.find('#qq_product_table')
                var $newLine= $(QWeb.render('QuickQuotationLine', {
                    'product_id' : product_id,
                    'product_name' : product_name,
                }))
                var $line = $newLine.appendTo($lineTable);
                if ($line.length > 0){
                    self.cart.push(product_id);
                }else{
                    self.displayNotification({ message: _t('Warning: Something went wrong !'), type: 'danger' });
                }
                
                var $addeBox = $(ev.currentTarget).parents('.qq_o_kanban_record');
                if (self.cart.includes(product_id)){
                    $addeBox.addClass('qq_record_selected');
                }
            }    
        },
        action_delete_from_cart: function(ev){
            var self =  this;
            ev.preventDefault();
            var product_id = ev.currentTarget.value;
            var removeLine = ev.target.closest('tr').remove();

            var deletedBox = self.$("[data-box_id='"+ product_id +"']");
            if (self.cart.includes(product_id)){
                var index = self.cart.indexOf(product_id);
                if (index > -1) {
                    self.cart.splice(index, 1);
                }
                $(deletedBox).removeClass('qq_record_selected');
            }            
        },
    });

    return QuickQuotationRenderer;
});