# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2012 Elico Corp. All Rights Reserved.
#    Author:            Yannick Gouin <yannick.gouin@elico-corp.com>
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
    "name" : "Display HTML",
    "version" : "1.2.0",
    "category" : "Hidden",
    "description" : """This module provides a  new widget to display HTML tags.
You need to add in your view's field widget="text_WYSIWYG" to see the result as HTML instead of text.

If you download and install the widget "web_wysiwyg", you can replace the basic texareas by powerful WYSIWYG editors.
""",
    "author": "Elico Corp",
    "website": "http://www.openerp.net.cn",
    "images" : [
        "images/result.png",
    ],
    "depends" : [],
    "js" : [
        "static/src/js/web_display_html.js",
    ],
    "css" : [
        "static/src/css/web_display_html.css",
    ],
    "init_xml" : [],
    "update_xml" : [],
    "demo_xml": [], 
    "test" : [],
    "auto_install" : True,
    "active" : True,
    "certificate" : "",
}
