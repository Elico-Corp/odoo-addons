# -*- coding: utf-8 -*-
# © 2017 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models,_
from odoo.exceptions import UserError
from lxml import etree

class ProjectTaskInherit(models.Model):
    _inherit = 'project.task'

    sub_extra_time = fields.Float(
        'Extra Time',help='the sum of the extra time',
        default='0',
    )

    @api.multi
    def write(self, vals):
        remaining = self.remaining_hours
        for record in vals.get('timesheet_ids'):
            if record[0] == 0:
                remaining -= record[2]['unit_amount']
            elif record[0] == 2:
                item = self.timesheet_ids.search([
                    ('id','=',record[1])
                ])
                remaining += item['unit_amount']
        if remaining < 0:
            raise UserError(
                _('The task have no enough time, please Apply for more extra time'))
        res = super(ProjectTaskInherit, self).write(vals)
        return res

    @api.multi
    def open_extra_time_line(self):
        for record in self:
            print record
            domain = [('task_no', '=', record.name)]
            return {
                'name': _('Extra Time Approve'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'extra.time.application',
                'target': 'current',
                'domain': domain,
            }

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ProjectTaskInherit, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        # if view_type == 'form':
        #     dom = etree.XML(res['arch'])
        #     for node in dom.xpath("//field[@name='remaining_hours']"):
        #         node.set("modifiers", '{"readonly": False}')
        #     res['arch'] = etree.tostring(dom)
        return res


# @api.model
# def fields_view_get(self, view_id=None, view_type='form',toolbar=False, submenu=False):
#     """Override method to change the modifier based on logged in user"""
#     res = super(WsOverview, self).
#     fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,submenu=submenu)
#     user_id = self.env['res.users'].browse(self._uid)
#     dom = etree.XML(res['arch'])
#     if user_id.has_group('crm_waste_application.waste_application_portal_user')
#         \and not user_id.has_group('crm_waste_application.waste_application_user'):
#         for node in dom.xpath("//field[@name='partner_id']"):
#             node.set("modifiers", '{"readonly": true}')
#         for node1 in dom.xpath("//field[@name='user_id']"):
#             node1.set("modifiers", '{"readonly": true}')
#         for node in dom.xpath("//field[@name='suez_number']"):
#             node.set("modifiers", '{"readonly": true}')
#     res['arch'] = etree.tostring(dom)
#     return res