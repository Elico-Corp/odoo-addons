openerp.auth_cas = function(instance) {
    var QWeb = instance.web.qweb,
        _t = instance.web._t;

    // Used for CAS authentication
    instance.web.login = instance.web.WebClient.extend({
        start: function () {
            var self = this;
            debugger;

            // If the url contains 'without_cas', we don't do anything
            // There is a bug if portal_anonymous is activated and there is no session, so we don't do anything in this case too
            if (location.search.lastIndexOf('without_cas') != -1 || (self.module_loaded['portal_anonymous'] && !this.session.username)){
                this._super();
            }
            else {
                self.$('.oe_login_form').hide();
                return $.when(self._super()).done(function () {
                    var dblist = self.db_list || [];
                    var dbname = self.params.db || (dblist.length === 1 ? dblist[0] : null);
                })
            }
        },

        // Redirects to CAS server
        do_redirect: function(host, port) {
            var self = this,
                callback_host = self.delCASTicket(),
				parser = document.createElement('a'),
				host_tmp = parser.href = host,
				host_to_redirect = parser.protocol + '//' + parser.hostname + ':' + port + parser.pathname  + '/login?service=' + encodeURIComponent(callback_host);
            $(location).attr('href', host_to_redirect);
        },

        // Get the ticket from url
        getCASTicket: function() {
            var params = location.search.substring(1).split('&'),
                ticket = false;
            for (var i=0; i<params.length; i++) {
                var arg = params[i].split('=');
                if(arg[0] == ('ticket'))
                    ticket = arg[1];
            }
            return ticket;
        },

        // Delete the ticket from url
        delCASTicket: function() {
            var params = location.search.substring(1).split('#')[0].split('&');
            if($(location).attr('href').lastIndexOf('#') == $(location).attr('href').length - 1) {
                var sharp = true;
            }
            if(location.search == '' || $(location).attr('href').split('?')[1] == '') {
                if(sharp)
                    return $(location).attr('href').split('#')[0].split('?')[0];
                else
                    return $(location).attr('href').split('?')[0] + document.location.hash;
            }
            if(params.length == 1 && params[0].substring(0,6) == 'ticket') {
                if(sharp)
                    return $(location).attr('href').split('#')[0].split('?')[0];
                else
                    return $(location).attr('href').split('?')[0] + document.location.hash;
            }

            var url = $(location).attr('href').split('?')[0] + '?',
                loop = 0;
            for (var i=0; i<params.length; i++) {
                var arg = params[i].split('=');
                if(arg[0] != ('ticket')) {
                    if(loop != 0)
                        url += '&';
                    url += arg[0] + '=' + arg[1];
                    loop++;
                }
            }
            if(sharp)
                return url.split('#')[0];
            else
                return url + document.location.hash;
        }
    });

    // Used for CAS deauthentication
    instance.web.WebClient = instance.web.WebClient.extend({
        // on_logout: function() {
        //     var self = this;
        //     var dbname;

        //     // Get the name of the database used
        //     self.rpc("/web/database/get_list", {})
        //         .done(function(result) {
        //             dbname = result[0];
        //             Logout the user
        //             if (!self.has_uncommitted_changes()) {
        //                 self.session.session_logout().done(function () {
        //                     $(window).unbind('hashchange', self.on_hashchange);
        //                     self.do_push_state({});

        //                     if (dbname) {
        //                         self.rpc("/auth_cas/get_config", {dbname: dbname})
        //                             .done(function(result) {
        //                                 // If the CAS authentication is enabled, logout from CAS server too
        //                                 if(result.login_cas == 'True')
        //                                     self.cas_logout(result.host, result.port);
        //                                 else
        //                                     window.location.reload();
        //                             });
        //                     }
        //                 });
        //             }
        //         });
        // },

        // Logout from CAS server
        cas_logout: function(host, port) {
            var callback_host = $(location).attr('href'),
				parser = document.createElement('a'),
				host_tmp = parser.href = host,
				host_to_redirect = parser.protocol + '//' + parser.hostname + '/logout?service=' + encodeURIComponent(callback_host);
            $(location).attr('href', host_to_redirect);
        }
    });

};
