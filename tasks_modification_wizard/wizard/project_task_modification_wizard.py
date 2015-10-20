# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields


class project_task_modification_wizard(osv.osv_memory):
    _name = "project.task.modification.wizard"
    _description = "Project task modification wizard"

    _columns = {
        'date_deadline': fields.date('Deadline'),
        'date_start': fields.date('Starting Date'),
        'date_end': fields.date('Ending Date'),
        'deadline_remove': fields.boolean('Remove Deadline'),
        'start_remove': fields.boolean('Remove Starting Date'),
        'end_remove': fields.boolean('Remove Ending Date'),
    }

    _defaults = {
        'deadline_remove': False,
        'start_remove': False,
        'end_remove': False,
    }

    def mass_modification(self, cr, uid, ids, context=None):
        data = {}

        for obj in self.browse(cr, uid, ids, context=context):
            if obj.date_deadline:
                data.update({'date_deadline': obj.date_deadline})
            if obj.date_start:
                data.update({'date_start': obj.date_start})
            if obj.date_end:
                data.update({'date_end': obj.date_end})
            if obj.deadline_remove:
                data.update({'date_deadline': False})
            if obj.start_remove:
                data.update({'date_start': False})
            if obj.end_remove:
                data.update({'date_end': False})
        task_pool = self.pool.get('project.task')
        task_pool.write(cr, uid, context['active_ids'], data, context=context)
