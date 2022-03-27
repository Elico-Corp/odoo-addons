odoo.define('disable_form_quick_edit.ListRenderer', function (require) {
"use strict";

let ListRenderer = require('web.ListRenderer');

ListRenderer.include({

    init: function (parent, state, params) {
        this._super.apply(this, arguments);
        if (this.getParent() && this.getParent().mode !== 'edit') {
            this.creates = [];
            this.addTrashIcon = false;
        }
    },

});

});