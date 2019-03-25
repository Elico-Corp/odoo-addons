// -*- coding: utf-8 -*-
// © 2015 Elico Corp (www.elico-corp.com).
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

function openerp_pos_quantity(instance, module){
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var orderline_id = 1;
    var test = 0;

    var Orderline = module.Orderline.extend({
        initialize: function(attr,options){
            Orderline.__super__.initialize.call(this, attr, options);
            this.sequence = 0;
        },

        get_sequence: function(){
            return this.sequence;
        },       
    });
    module.Orderline = Orderline;

    // 7572-Siyuan: return the total quantity for the order module
    module.Order = module.Order.extend( {
        getTotalQuantity: function() {
            return (this.get('orderLines')).reduce((function(sum, orderLine) {
                return sum + orderLine.get_quantity();
            }), 0);
        },       
    });

    module.OrderWidget = module.OrderWidget.extend({
        remove_orderline: function(order_line){
            if(this.pos.get('selectedOrder').get('orderLines').length === 0){
                this.renderElement();
            }else{
                order_line.node.parentNode.removeChild(order_line.node);

                // 7572-Siyuan: refresh the sequence when order line is deleted
                this.renderElement();
            }
        },

        renderElement: function(scrollbottom){
            this.pos_widget.numpad.state.reset();

            var order  = this.pos.get('selectedOrder');
            var orderlines = order.get('orderLines').models;

            var el_str  = openerp.qweb.render('OrderWidget',{widget:this, order:order, orderlines:orderlines});

            var el_node = document.createElement('div');
                el_node.innerHTML = _.str.trim(el_str);
                el_node = el_node.childNodes[0];


            var list_container = el_node.querySelector('.orderlines');
            for(var i = 0, len = orderlines.length; i < len; i++){

                // 7572-Siyuan: add the sequence number for order line
                orderlines[i].sequence = i + 1;

                var orderline = this.render_orderline(orderlines[i]);
                list_container.appendChild(orderline);
            }

            if(this.el && this.el.parentNode){
                this.el.parentNode.replaceChild(el_node,this.el);
            }
            this.el = el_node;
            this.update_summary();

            if(scrollbottom){
                this.el.querySelector('.order-scroller').scrollTop = 100 * orderlines.length;
            }
        },

        update_summary: function(){
            var order = this.pos.get('selectedOrder');
            var total     = order ? order.getTotalTaxIncluded() : 0;
            var taxes     = order ? total - order.getTotalTaxExcluded() : 0;
            var quantity  = order ? order.getTotalQuantity() : 0;

            // 7572-Siyuan: set the total quantity when the summary is updated
            this.el.querySelector('.summary .total .quantity').textContent = quantity;

            this.el.querySelector('.summary .total .value').textContent = this.format_currency(total);
            this.el.querySelector('.summary .total .subentry .value').textContent = this.format_currency(taxes);

        },
    });
}
