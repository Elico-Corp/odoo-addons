/******************************************************************************
*
*    OpenERP, Open Source Management Solution
*    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
*    Augustin Cisterne-Kaas <augustin.cisterne-kaas@elico-corp.com>
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU Affero General Public License as
*    published by the Free Software Foundation, either version 3 of the
*    License, or (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU Affero General Public License for more details.
*
*    You should have received a copy of the GNU Affero General Public License
*    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
******************************************************************************/
openerp.mail_organizer = function (instance) {
    var mail = instance.mail;
    var QWeb = instance.web.qweb;
    window.yep = instance;
    mail.ThreadMessage = mail.ThreadMessage.extend({
        template: 'mail.thread.message',
        events: {
                   'click .oe_assign': 'open_wizard',
        },

        start: function () {
            this._super.apply(this, arguments);
        },

        open_wizard: function() {
            var self = this;
            var context = {
                       'active_id': this.id,
            };
            var action = {
                            type: 'ir.actions.act_window',
                            res_model: 'wizard.mail.organizer',
                            view_mode: 'form',
                            view_type: 'form',
                            views: [[false, 'form']],
                            target: 'new',
                            context: context,
                    };
            self.do_action(action);
        }

    });
};