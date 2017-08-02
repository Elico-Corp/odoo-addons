/*---------------------------------------------------------
 * OpenERP web_display_html
 *---------------------------------------------------------*/

openerp.web_display_html = function (openerp) {
    openerp.web.form.widgets.add('text_WYSIWYG', 'openerp.web.form.FieldText');
    openerp.web.page.readonly.add('text_WYSIWYG', 'openerp.web_display_html.FieldWYSIWYGReadonly');

    openerp.web_display_html = {};
    openerp.web_display_html.FieldWYSIWYGReadonly = openerp.web.page.FieldCharReadonly.extend({
        template: 'FieldChar.readonly',
        init: function(view, node) {
            this._super(view, node);
        },
        set_value: function (value) {
            this._super.apply(this, arguments);
            var show_value = openerp.web.format_value(value, this, '');

            // for security, we remove all the dangerous tags
            show_value = show_value.replace(/<applet.*<\/applet>/gi, '');
            show_value = show_value.replace(/<body.*>/gi, '');
            show_value = show_value.replace(/<\/body>/gi, '');
            show_value = show_value.replace(/<head.*>/gi, '');
            show_value = show_value.replace(/<\/head>/gi, '');
            show_value = show_value.replace(/<embed.*<\/embed>/gi, '');
            show_value = show_value.replace(/<frame.*<\/frame>/gi, '');
            show_value = show_value.replace(/<frameset.*<\/frameset>/gi, '');
            show_value = show_value.replace(/<html.*>/gi, '');
            show_value = show_value.replace(/<\/html>/gi, '');
            show_value = show_value.replace(/<iframe.*<\/iframe>/gi, '');
            show_value = show_value.replace(/<layer.*<\/layer>/gi, '');
            show_value = show_value.replace(/<link.*<\/link>/gi, '');
            show_value = show_value.replace(/<ilayer.*<\/ilayer>/gi, '');
            show_value = show_value.replace(/<meta.*<\/meta>/gi, '');
            show_value = show_value.replace(/<object.*<\/object>/gi, '');
            show_value = show_value.replace(/<script.*<\/script>/gi, '');
            show_value = show_value.replace(/(<applet|body|head|embed|frame|frameset|html|iframe|layer|link|ilayer|meta|object|script).*\/>/gi, '');
            // for security, we remove all the dangerous event which could have been added
            show_value = show_value.replace(/(onabort|onblur|onchange|onclick|ondblclick|onerror|onfocus|onkeydown|onkeypress|onkeyup|onload|onmousedown|onmousemove|onmouseout|onmouseover|onmouseup|onreset|onresize|onselect|onsubmit|onunload)/gi, 'forbiden');

            this.$element.find('div').html(show_value);
            return show_value;
        }
    });
};


