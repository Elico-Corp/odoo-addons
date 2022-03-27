odoo.define('disable_form_quick_edit.FormController', function (require) {
"use strict";

let FormController = require('web.FormController');

FormController.include({
    _onQuickEdit: function () {},
});

});