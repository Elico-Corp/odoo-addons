odoo.define("auth_cas.auth_cas", function (require) {
    "use strict";

    var core = require("web.core");
    var tour = require("web_tour.tour");
    var base = require("web_editor.base");
    var Session = require("web.Session");
    var QWeb = core.qweb;
    var _t = core._t;

    Session.include({
        setup: function(origin, options) {
            // must be able to customize server
//            var window_origin = location.protocol + "//" + location.host;
//            origin = origin ? origin.replace( /\/+$/, '') : window_origin;
//            if (!_.isUndefined(this.origin) && this.origin !== origin)
//                throw new Error('Session already bound to ' + this.origin);
//            else
//                this.origin = origin;
//            this.prefix = this.origin;
//            this.server = this.origin; // keep chs happy
//            this.origin_server = this.origin === window_origin;
//            options = options || {};
//            if ('use_cors' in options) {
//                this.use_cors = options.use_cors;
//            }

            var self = this;
            debugger;

            // If the url contains 'without_cas', we don't do anything
            // There is a bug if portal_anonymous is activated and there is no session, so we don't do anything in this case too
            if (location.search.lastIndexOf('without_cas') != -1 || (self.module_loaded['portal_anonymous'] && !this.session.username)){
                this._super.apply(this, arguments);
            }
            else {
                self.$('.oe_login_form').hide();
                return $.when(self._super()).done(function () {
                    var dblist = self.db_list || [];
                    var dbname = self.params.db || (dblist.length === 1 ? dblist[0] : null);
                })
            }
        },
    });

});