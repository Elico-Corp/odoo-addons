function openerp_pos_membership (instance, module){
        var _t = instance.web._t;
        var QWeb = instance.web.qweb;

    // customer screen widget
    module.ClientListScreenWidget = module.ClientListScreenWidget.extend({
        show: function(){
            /// force update the partner before display in order to keep the VIP account balance
            this._super();
            self=this;
            this.disable_membership_balance_before_loading();
            var partners = this.pos.db.get_partners_sorted(1000);
            var partners_ids = [];
            for (var i=0; i<partners.length; i++)
                partners_ids.push(partners[i].id);
            this.pos.load_new_partners_by_ids(partners_ids).done(function(){
                var new_partners = self.pos.db.get_partners_sorted(1000);
                self.render_list(new_partners);
            }).fail(function(){
                self.error_membership_balance_when_loading();
            });
        },
        disable_membership_balance_before_loading: function() {
            // replace the values in the list view.
            membership_balance_contents = this.$el[0].querySelectorAll('.membership_balance');
            for (var i = 0; i < membership_balance_contents.length; i++){
                membership_balance_contents[i].innerHTML = "<div class='.oe_loading'>Loading...<div/>";
            }
        },
        error_membership_balance_when_loading: function() {
            // replace the values in the list view.
            membership_balance_contents = this.$el[0].querySelectorAll('.membership_balance');
            for (var i = 0; i < membership_balance_contents.length; i++){
                membership_balance_contents[i].innerHTML = "<div class='.oe_loading' style ='color: red'>Offline!<div/>";
            }
        },
        save_changes: function(){
            // empty all the payment lines when the customer has changed.
            if (this.has_client_changed()) {
                var currentOrder = this.pos.get('selectedOrder');
                currentOrder.removeAllPaymentLines();
            }
            this._super();
        }
    });

    // add membership related fields into the fetch list of models.
    (function() {
        models = module.PosModel.prototype.models;
        if (models) {
            for (var i=0; i<models.length; i++) {
                if (models[i]['model'] == 'product.product') {
                    fields = models[i]['fields'];
                    // add the new field to fetch.
                    fields.push('membership');
                    module.PosModel.prototype.models[i]['fields'] = fields;
                } else if ( models[i]['model'] == 'account.journal'){
                    fields = models[i]['fields'];
                    // add the new field to fetch.
                    fields.push('membership');
                    fields.push('name');
                    fields.push('type');
                } else if (models[i]['model'] == 'res.partner') {
                    fields = models[i]['fields'];
                    fields.push('membership_total_future');
                    fields.push('id');
                }
            };
        };
    })();

    module.PosModel = module.PosModel.extend({
        // reload the list of partner, returns as a deferred that resolves if there were
        // updated partners, and fails if not
        // need to update the membership balance every time you access the partners.
        load_new_partners_by_ids: function(ids){
            var self = this;
            var def  = new $.Deferred();
            var fields = _.find(this.models,function(model){ return model.model === 'res.partner'; }).fields;
            defer = new instance.web.Model('res.partner')
                .query(fields)
                .filter([['id', 'in', ids]])
                .all({'timeout':3000, 'shadow': true})
                .then(function(partners){
                    for (var i=0; i<partners.length; i++) {
                        var partner = partners[i];
                        if (!self.db.partner_by_id[partner.id]) {
                            self.db.partner_sorted.push(partner.id);
                        };
                        self.db.partner_by_id[partner.id] = partner;
                        self.db.partner_write_date = partner.partner_write;
                    }
                    self.db.partner_search_string = "";
                    self.db.partner_by_ean13 = {};

                    for (var id in self.db.partner_by_id) {
                        var partner = self.db.partner_by_id[id];

                        if(partner.ean13){
                            self.db.partner_by_ean13[partner.ean13] = partner;
                        }
                        partner.address = (partner.street || '') +', '+ 
                                          (partner.zip || '')    +' '+
                                          (partner.city || '')   +', '+ 
                                          (partner.country_id[1] || '');
                        self.db.partner_search_string += self.db._partner_search_string(partner);
                    }
                    def.resolve();
                }, function(err,event){ event.preventDefault(); def.reject(); });
            return def;
        },
    });

    module.Paymentline = module.Paymentline.extend({
        // is VIP card payment method or not.
        is_membership: function() {
            return this.cashregister.journal.membership
        },
    });

    module.PaymentScreenWidget = module.PaymentScreenWidget.extend({
        validate_order: function(options) {
            // check if user try to pay membership product with membership journal.
            var self = this;
            options = options || {};
            var currentOrder = this.pos.get('selectedOrder');
            // cannot charge for VIP card without selecting a customer.
            if (currentOrder.is_there_membership_product()) {
                if (this.pos.get('selectedOrder').get('client') == null) {
                    this.pos_widget.screen_selector.show_popup('error',{
                         'message': _t('Error'),
                         'comment': _t('You must select a customer before charging VIP card!'),
                     });
                     return; 
                }
            }
            // if pay with membership journal
            if (currentOrder.is_there_membership_journal()) {
                // if pay membership product with membership journal, block!
                if (currentOrder.is_there_membership_product()) {
                    this.pos_widget.screen_selector.show_popup('error',{
                        'message': _t('Error'),
                        'comment': _t('Cannot pay for membership products with VIP Card!'),
                    });
                    return;
                };
                // If there is no partner selected, block!
                if (this.pos.get('selectedOrder').get('client') == null) {
                    this.pos_widget.screen_selector.show_popup('error',{
                        'message': _t('Error'),
                        'comment': _t('You must select a customer before paying by VIP card!'),
                    });
                    return;
                };
                // if enough balance;
                if (currentOrder.get_client_membership_balance() < currentOrder.get_paid_membership_amount()) {
                    this.pos_widget.screen_selector.show_popup('error',{
                        'message': _t('Error'),
                        'comment': _t('No enough membership balance!')
                    });
                    return;
                }
            };
            // call parent method.
            this._super.apply(this, arguments);
        }
    });

    var Order = module.Order.extend({
        // add a new method to remove all the payment lines in a order
        removeAllPaymentLines: function() {
            lines = this.get('paymentLines').models.slice(0);
                for (var i=0; i<lines.length; i++) {
                    var line = lines[i];
                    this.removePaymentline(line);
                }
        },
        // check if there is VIP card payment method in the payment lines of current order;
        is_there_membership_journal: function (){
            plines = this.get('paymentLines').models;
            for (var i=0; i<plines.length; i++) {
                journal = plines[i].cashregister.journal;
                if (journal.membership) {
                    return true;
                }
            }
            return false;
        },
        // check if there is membership product in current order;
        is_there_membership_product: function(){
            orderLines = this.get('orderLines').models;
            for (var i=0; i<orderLines.length; i++) {
                product = orderLines[i]['product'];
                if (product['membership']) {
                    return true;
                }
            }
            return false;
        },
        get_client_membership_balance: function(){
            var client = this.get_client();
            var new_client = {'membership_total_future': 0};
            if (client) {
                id = client.id;
                this.pos.load_new_partners_by_ids([id]);
                new_client = this.pos.db.partner_by_id[id];
            }
            return new_client['membership_total_future'];
        },
        get_client_membership_balance_cached: function(){
            var client = this.get_client();
            if (client) {
                var id = client.id;
                var new_client = this.pos.db.partner_by_id[id];
                return new_client['membership_total_future'];
            }
            return 0;
        },
        get_paid_membership_amount: function() {
            // go through all other payment lines, to check if the same membership journal
            plines = this.get('paymentLines').models;
            paid_membership_total = 0.0;
            // pline
            // node['isContentEditable']
            for (var i=0; i<plines.length; i++) {
                if (plines[i].is_membership()) {
                    paid_membership_total += plines[i].get_amount();
                }
            }
            return paid_membership_total;
        },
        addPaymentline: function (cashregister){
            // first we check the balance if the payment method is VIP card.
            if (cashregister.journal.membership !== true) {
                Order.__super__.addPaymentline.call(this, cashregister);
            }
            else {
                var paymentLines = this.get('paymentLines');
                amount = Math.max(this.getDueLeft(),0);
                paid_membership_total = this.get_paid_membership_amount();

                // check the balance of this client.
                client = this.get_client();
                client_membership_balance = this.get_client_membership_balance();
                if (client) {
                    balance = (client_membership_balance - paid_membership_total) || 0;
                    if (balance < 0) {
                        this.pos.pos_widget.screen_selector.show_popup('error',{
                            'message': _t('Error'),
                            'comment': _t('No enough balance in the VIP card!'),
                        });
                        return false;
                    };
                    if (balance < amount) amount = client_membership_balance-paid_membership_total;
                }
                else {
                    this.pos.pos_widget.screen_selector.show_popup('error',{
                        'message': _t('Error'),
                        'comment': _t('Select a customer first!'),
                    });
                    return false;
                }
                var newPaymentline = new module.Paymentline({},{cashregister:cashregister, pos:this.pos});
                newPaymentline.set_amount(amount);
                paymentLines.add(newPaymentline);
                this.selectPaymentline(newPaymentline);
            }
        }
    })
    module.Order  = Order;

    module.PosDB = module.PosDB.extend({

        force_update_partners: function(partners){
            var updated_count = 0;
            var new_write_date = '';
            for(var i = 0, len = partners.length; i < len; i++){
                var partner = partners[i];
                new_write_date  = partner.write_date;
                if (!this.partner_by_id[partner.id]) {
                    this.partner_sorted.push(partner.id);
                }
                this.partner_by_id[partner.id] = partner;

                updated_count += 1;
            }

            this.partner_write_date = new_write_date || this.partner_write_date;

            if (updated_count) {
                // If there were updates, we need to completely 
                // rebuild the search string and the ean13 indexing

                this.partner_search_string = "";
                this.partner_by_ean13 = {};

                for (var id in this.partner_by_id) {
                    var partner = this.partner_by_id[id];

                    if(partner.ean13){
                        this.partner_by_ean13[partner.ean13] = partner;
                    }
                    partner.address = (partner.street || '') +', '+ 
                                      (partner.zip || '')    +' '+
                                      (partner.city || '')   +', '+ 
                                      (partner.country_id[1] || '');
                    this.partner_search_string += this._partner_search_string(partner);
                }
            }
            return updated_count;
        },
    });

module.PaypadButtonWidget = module.PaypadButtonWidget.extend({
        renderElement: function() {
            var self = this;
            this._super();

            this.$el.click(function(){
                // need to select customer first if you choose VIP card payment method.
                currentOrder = self.pos.get('selectedOrder');
                if (self.cashregister.journal.membership && currentOrder.get('client') == null) {
                    self.pos_widget.screen_selector.show_popup('error',{
                        'message': _t('Error'),
                        'comment': _t('You must select a customer before paying by VIP card!'),
                    });
                    return;
                };
            });
        },
    });

};

openerp.pos_membership = function(instance){

    var module = instance.point_of_sale;

    openerp_pos_membership(instance,module);
};