odoo.define('products_quick_quotation.QuickQuotationModel', function (require) {
    "use strict";

    var AbstractModel = require('web.AbstractModel');

    var QuickQuotationModel = AbstractModel.extend({
        init: function () {
            this._super.apply(this, arguments);
            this.quotation = null;
            this.pager_count = null;
            this.res_partner = false;
        },  
        __get: function () {
            var result = this._super.apply(this, arguments);
            if (result) {
                _.extend(result, this.quotation, {
                    fields: this.fields,
                    res_partner: this.res_partner,
                });
            }
            return result;
        },

        __load: function (params) { 
            var self = this;           
            this.fields = params.fields;
            this.modelName = params.modelName;
            
            if (!this.preloadPromise) {
                this.preloadPromise = new Promise(function (resolve, reject) {
                    Promise.all([
                        self._rpc({
                            model: 'product.product', 
                            method: 'search_read',  
                            kwargs: {
                                domain: params.domain
                            },
                        }),
                        self._rpc({
                            model: 'res.partner', 
                            method: 'search_read', 
                            args: [[]], 
                            kwargs: { 
                                fields: ['id','name'] 
                            },
                        }),
                    ]).then(function (result) {
                        var pager_count = result[0];
                        var res_partner = result[1];
                        self.pager_count = pager_count.length;
                        self.res_partner = res_partner;
                        resolve();
                    }).guardedCatch(reject);
                })
            }
            this.quotation = {
                modelName: this.modelName,
                data: [],
                domain: params.domain,
                context: params.context,
                limit: params.limit,
                offset: params.offset || 0,                
            };
            return this.preloadPromise.then(this._fetchData.bind(this));
        },
        _fetchData: function () {
            return this._rpc({
                model: 'product.product',
                method: 'search_read',
                kwargs: {
                    domain: this.quotation.domain,
                    limit: this.quotation.limit,
                    offset: this.quotation.offset,
                    context: this.quotation.context,
                }
            })
            .then(this._parseData.bind(this));
        },
        __reload: function (handle, params) {
            var self = this;
            if ('domain' in params) {
                this.quotation.domain = params.domain;
            }            
            if ('context' in params) {
                this.quotation.context = params.context;
            }
            if ('offset' in params) {
                this.quotation.offset = params.offset;
            }          
            if ('limit' in params) {
                this.quotation.limit = params.limit;
            }            
            if (this.preloadPromise) {
                this.preloadPromise = new Promise(function (resolve, reject) {
                    Promise.all([
                        self._rpc({
                            model: 'product.product', 
                            method: 'search_read',  
                            kwargs: {domain: params.domain}
                        }),
                    ]).then(function (result) {
                        var pager_count = result[0].length;
                        self.pager_count = pager_count;
                        resolve();
                    }).guardedCatch(reject);
                })
            }
            return this.preloadPromise.then(this._fetchData.bind(this));
        },        
        _parseData: function (data) {
            this.quotation.data = [];
            if (!data) {
                return;
            }
            for (let j = 0; j < data.length; j++) {
                let product = {
                    id: data[j]['id'].toString(),
                    name: data[j]['name'],
                    display_name: data[j]['display_name'],
                    image_medium: data[j]['image_128'],                    
                    list_price: parseFloat(data[j]['list_price']).toFixed(2),
                    currency_id: data[j]['currency_id'],
                };
                this.quotation.data.push(product);
            }
        },
    });
    return QuickQuotationModel;
});