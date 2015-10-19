# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Chen Rong <chen.rong@elico-corp.com>
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
from openerp.osv import fields, orm


class project_task(orm.Model):
    _inherit = 'project.task'

    def _get_git_branch(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            name = "%s-%s" % (task.id, task.name)
            name = name.replace(" ", "-")
            res[task.id] = name.lower()
        return res

    def _get_git_environment(self, cr, uid, context=None):
        return [
            ('trunk', 'Trunk'),
            ('release', 'Release'),
            ('stable', 'Stable')]

    def _get_source_branch(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            if not task.git_environment:
                continue
            res[task.id] = getattr(
                task.project_id, 'git_%s' % task.git_environment)
        return res

    def onchange_gsb(self, cr, uid, ids, project_id, git_environment):
        if git_environment and project_id:
            project_obj = self.pool.get('project.project')
            project = project_obj.browse(cr, uid, project_id)
            git_source_branch = getattr(project, 'git_%s' % git_environment)
            return {'value': {'git_source_branch': git_source_branch}}
        return {}

    def onchange_project(self, cr, uid, ids, project_id, ):
        res = super(project_task, self).onchange_project(
            cr, uid, ids, project_id)
        if 'value' not in res:
            res['value'] = {}
        if not project_id:
            return res
        project_obj = self.pool.get('project.project')
        project = project_obj.browse(cr, uid, project_id)
        res['value']['git_environment'] = project.git_default
        gsb = self.onchange_gsb(cr, uid, ids, project_id, project.git_default)
        if 'value' in gsb:
            res['value']['git_source_branch'] = \
                gsb['value']['git_source_branch']
        return res

    def _git_instruction(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            if not task.git_environment:
                continue
            branch_src = task.git_source_branch
            branch = task.git_branch
            res[task.id] = """
            git checkout %s
            git fetch upstream
            git merge upstream/%s
            git checkout -b %s origin/%s
            """ % (branch_src, branch_src, branch, branch_src)
        return res

    _columns = {
        'git_branch': fields.function(
            _get_git_branch, type='char', method=True, string='Git branch',
            store={
                'project.task': (
                    lambda self, cr, uid, ids, c={}: ids, ['name'], 10),
            }),
        'git_environment': fields.selection(
            _get_git_environment, 'Git environment'),
        'git_source_branch': fields.char(string='Git Source Branch'),
        'git_instruction': fields.function(
            _git_instruction, type='text', method=True,
            string='Git Instruction',
            store={
                'project.task': (
                    lambda self, cr, uid, ids, c={}: ids,
                    ['git_source_branch', 'git_branch'], 10)
            })

    }
