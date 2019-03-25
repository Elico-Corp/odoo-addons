# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv, fields


class ProjectTaskModificationWizard(osv.osv_memory):
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
