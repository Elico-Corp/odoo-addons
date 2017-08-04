# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)

{
    "name": "Pos Mall Report",
    "version": "7.0.1.0.0",
    "author": "Elico Corp",
    "website": "https://www.elico-corp.com",
    "description": """
    """,
    "depends": ['point_of_sale'],
    "category": "Sales",
    "update_xml": ["security/pos_mall_report_security.xml",
                   "security/ir.model.access.csv",
                   "wizard/upload_mall_file_view.xml",
                   "pos_mall_report_data.xml",
                   "pos_mall_report_view.xml",
                   "pos_mall_report_sequence.xml"],
    "license": "AGPL-3",
    "active": False,
    "installable": True
}
