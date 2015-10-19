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


class project_project(orm.Model):
    _inherit = 'project.project'

    def _get_git_environment(self, cr, uid, context=None):
        return [
            ('trunk', 'Trunk'),
            ('release', 'Release'),
            ('stable', 'Stable')]
    _columns = {
        'git_trunk': fields.char('Git Trunk'),
        'git_release': fields.char('Git Release'),
        'git_stable': fields.char('Git Stable'),
        'git_default': fields.selection(_get_git_environment, 'Git Default')
    }
