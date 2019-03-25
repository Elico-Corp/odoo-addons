# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, orm


class ProjectProject(orm.Model):
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
