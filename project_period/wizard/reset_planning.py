# -*- coding: utf-8 -*-
# © 2015-2017 Elico corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class WizardResetPlanning(models.TransientModel):
    _name = 'wizard.reset.planning'

    @api.multi
    def reset_planning(self):
        tasks = self.env['project.task'].search([])
        tasks.write({
            'week_1': 0,
            'week_2': 0,
            'week_3': 0,
            'week_4': 0,
        })
        return True
