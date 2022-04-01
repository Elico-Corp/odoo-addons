odoo.define('products_quick_quotation.QuickQuotationView', function (require) {
    "use strict";
        
        var view_registry = require('web.view_registry');
        var core = require('web.core');
        var _lt = core._lt;
        var AbstractView = require('web.AbstractView');

        var QuickQuotationRenderer = require('products_quick_quotation.QuickQuotationRenderer');
        var QuickQuotationModel = require('products_quick_quotation.QuickQuotationModel');
        var QuickQuotationController = require('products_quick_quotation.QuickQuotationController');
        var view_registry = require('web.view_registry');
    
        var QuickQuotationView = AbstractView.extend({
            display_name: _lt('Quick Quotation View'),
            icon: 'fa-shopping-cart',
            jsLibs: [],
            cssLibs: [
                '/products_quick_quotation/static/src/css/style.css',
            ],
            accesskey: "k",
            config: _.extend({}, AbstractView.prototype.config, {
                Model: QuickQuotationModel,
                Controller: QuickQuotationController,
                Renderer: QuickQuotationRenderer,
            }),            
            viewType: 'quickquotationview',
            searchMenuTypes: ['filter', 'favorite',],
            
            init: function (viewInfo, params) {                
                this._super.apply(this, arguments);

                this.loadParams.context = params.context || {};   
                this.loadParams.fieldsInfo = viewInfo.fieldsInfo;
                this.loadParams.fields = viewInfo.fields;
                

                this.loadParams.limit = this.loadParams.limit || 30;
                this.controllerParams.withButtons = 'action_buttons' in params ? params.action_buttons : true;
            },  
        
        });  
        view_registry.add('quickquotationview', QuickQuotationView);
    });