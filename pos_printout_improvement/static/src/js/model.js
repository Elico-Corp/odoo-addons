function openerp_pos_printout_improvement(instance, module){
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var orderline_id = 1;
    var test = 0;

    module.Order = module.Order.extend( {
        getTotalQuantity: function() {
            return (this.get('orderLines')).reduce((function(sum, orderLine) {
                return sum + orderLine.get_quantity();
            }), 0);
        },
    });
}