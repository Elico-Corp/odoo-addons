odoo.define('products_quick_quotation.QuickQuotationController', function (require) {
    "use strict";
    
    var AbstractController = require('web.AbstractController');
    var FieldManagerMixin = require('web.FieldManagerMixin');
    
    var rpc = require('web.rpc');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;
    
    var QuickQuotationController = AbstractController.extend(FieldManagerMixin, {
        className: 'quickquotation',
        xmlDependencies: ['/products_quick_quotation/static/src/xml/quick_quotation.xml'],
        custom_events: _.extend({}, AbstractController.prototype.custom_events, FieldManagerMixin.custom_events, {
            pager_changed: '_onPagerChanged',            
        }),
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            this.withButtons = params.withButtons;
            this.res_partner = model.res_partner;        
        },
        start: async function () {        
            await this._super(...arguments);            
        },  
        renderButtons: function ($node) {
            this.$buttons = $(qweb.render('QuickQuotation.buttons', this));
            this.$buttons.find('button').tooltip();
            this.$buttons.on('click', 'button.quick-quotation-new', this.actionQuickQuotation.bind(this));
            if (this.$buttons && $node) {
                this.$buttons.appendTo($node);
            }     
        },
        updateBoxStyle: function(){
            var self = this;
            var $productsArea = this.renderer.$el && this.renderer.$('div[id="qq_product_box"]');
            if ($productsArea.length){
                var self = this;
                _.each($productsArea, function(product){                
                    const product_id = product.getAttribute('data-box_id');
                    if (self.renderer.cart.includes(product_id)){
                        $(product).addClass('qq_record_selected');
                    }                    
                })
            }
        },
        updateButtons: function () {
            if (!this.$buttons) {
                return;
            }
            this.updateBoxStyle();            
        },    
        _getPagingInfo: function (state) {           
            return {
                currentMinimum: state.offset + 1,
                limit: state.limit,
                size: this.model.pager_count,
            };
        },
        _updateControlPanel: function (newProps = {}) {
            const state = this.model.get(this.handle);        
            const pagerProps = Object.assign(newProps, {
                actionMenus: this._getActionMenuItems(state),
                pager: this._getPagingInfo(state),
                title: this.getTitle(),
            });
            return this.updateControlPanel(pagerProps);
        },
        _onPagerChanged: async function (ev) {
            ev.stopPropagation();
            
            const { currentMinimum, limit } = ev.data;            
            const domain = this.model.quotation.domain;            
            const reloadParams = {
                    limit,
                    offset: currentMinimum - 1,
                    domain: domain,
                };
            await this.reload(reloadParams);

            const state = this.model.get(this.handle, { raw: true });       
            if (state.limit === limit) {
                this.trigger_up('scrollTo', { 
                    top: 0 
                });
            }
            this.updateBoxStyle();
        },
        actionQuickQuotation: function(ev){
            ev.preventDefault();
            ev.stopPropagation();
            var self =  this;
            var products = [];
            var model = self.modelName;
            var customer = self.$el.find('#quick_quotation_customer').val();

            var option = this.$(ev.currentTarget).data('option');
    
            if(customer == 'all_customers' || customer == undefined || customer == 'NaN'){
                self.displayNotification({ message: _t('Warning: Please Select a Customer'), type: 'danger' });
                return false;     
            }
    
            if($('#qq_product_table tbody tr').length > 0){
                this.$('#qq_product_table tbody tr').each(function() {
                    var product_id = $(this).find('#line_product_id')[0].innerHTML;  
                    var product_qty = $(this).find('#line_product_qty').val();

                    if (product_id && product_qty){
                        products.push({
                            product_id : parseInt(product_id),
                            product_qty : parseInt(product_qty),
                        });
                    }
                });                            
            }
            else {
                self.displayNotification({ message: _t('Warning: Please Select Products'), type: 'danger' });
            }

            if (products && customer && model){
                if (option === 'so'){
                    rpc.query({
                        model: 'sale.order',
                        method: 'create_quick_quotation',
                        args: [products,parseInt(customer),model]
                    }).then(function (returned_value) {                    
                        if (returned_value){
                            self.do_action({
                                type: 'ir.actions.act_window',
                                res_model: 'sale.order',
                                views: [[false, 'form']],
                                res_id: returned_value,                           
                                target: 'current',
                            });
                            $('#qq_product_table tr').not(function(){ 
                                return !!$(this).has('th').length; 
                            }).remove();
                            self.$buttons.find('#quick_quotation_customer').val('all_customers');
                            self.renderer.cart = [];
                        }                
                    });
                }else if (option === 'po'){
                    rpc.query({
                        model: 'purchase.order',
                        method: 'create_quick_quotation',
                        args: [products,parseInt(customer),model]
                    }).then(function (returned_value) {                    
                        if (returned_value){
                            self.do_action({
                                type: 'ir.actions.act_window',
                                res_model: 'purchase.order',
                                views: [[false, 'form']],
                                res_id: returned_value,                           
                                target: 'current',
                            });
                            $('#qq_product_table tr').not(function(){ 
                                return !!$(this).has('th').length; 
                            }).remove();
                            self.$buttons.find('#quick_quotation_customer').val('all_customers');
                            self.renderer.cart = [];
                        }                
                    });
                }                
            }
        },
    });
    return QuickQuotationController;
    });
    