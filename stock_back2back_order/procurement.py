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

from osv import osv, fields
import netsvc

class StockPicking(osv.osv):
    _inherit = 'stock.picking'

    def test_backorder_finished(self, cursor, user, ids):
        wf_service = netsvc.LocalService("workflow")
        proc_obj = self.pool.get('procurement.order')
        res = super(StockPicking, self).test_finished(cursor, user, ids)
        for picking in self.browse(cursor, user, ids):
            for move in picking.move_lines:
                # Update procurement.move_id for new moves. Ian@Elico
                if move.next_move and move.procurements:
                    for procurement in move.procurements:
                        proc_obj.write(cursor, user, [procurement.id], {'move_id': move.next_move.id})
                if not move.next_move and move.state == 'done' and move.procurements:
                    for procurement in move.procurements:
                        wf_service.trg_validate(user, 'procurement.order',
                                procurement.id, 'button_check', cursor)
        return res

StockPicking()