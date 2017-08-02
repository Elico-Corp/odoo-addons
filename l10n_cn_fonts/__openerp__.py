# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2011 Elico Corp. All Rights Reserved.
#    Author:            Eric CAUDAL <contact@elico-corp.com>
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
    "name" : "Chinese TrueType fonts",
    "version" : "1.0",
    "author" : "Elico Corp",
    "website" : "http://www.openerp.net.cn",
    "description": """
    This module replaces the standard PDF Type1 fonts with TrueType fonts that have
    unicode characters for simplified Chinese.
    The module contains the VeraSansYuanTi.
    With this module you can continue to use the old font names in the templates,
    they will be replaced with the Vera Sans Yuan Ti font names every time before creating a pdf.
    If you wish to use your own fonts, you have to place them in addons/l10_cn_fonts directory and 
    replace the font name in the file __init__.py accordingly.
    This Module is based on Gábor Dukai module (base_report_Unicode)
    """,
    "depends" : ["base", ],
    "category" : "Localization",
    "demo_xml" : [],
    "update_xml" : [],
    "license": "AGPL-3",
    "active": False,
    "installable": True
}
