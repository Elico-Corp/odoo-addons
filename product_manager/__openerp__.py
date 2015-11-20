# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Xia.Fajin
#    Email: xia.fajin@elico-corp.com
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

{
    "name": "Product Manager",
    "description": """

    Build ACL for products.
========================================================
                    """,
    "version": "0.1",
    "depends": ["product", "purchase", "stock", "mrp", "base", ],
    "category": "product",
    "author": "elico-corp",
    "url": "http://www.elico-corp.com/",
    "data": [
        'data/res_group_data.xml',
        'security/ir.model.access.csv',
    ],
    "installable": True,
    "auto_install": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
