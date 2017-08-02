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
    "name" : "WYSIWYG editor for web",
    "version" : "1.2.1",
    "category" : "Hidden",
    "description" : """This module provides a WYSIWYG editor (CKeditor).
You need to add in your view's field widget="text_WYSIWYG" to turn the classic textareas into powerful WYSIWYG editors.
Then add the following code in those views (this code add the button to switch on/off the WYSIWYG mode)

<html>
    <a onclick="javascript:toggle_ckeditor();" class="wysiwyg_button wysiwyg_button_off oe_button">WYSIWYG on</a>
</html>

So now, in your view you can enable or disable the WYSIWYG editors.

If you download and install the widget "web_display_html", your fields with widget="text_WYSWYG" will display the HTML instead of the basic text with the tags.
""",
    "author": "Elico Corp",
    "website": "http://www.openerp.net.cn",
    "images" : [
        "images/wysiwyg_on.png",
        "images/wysiwyg_off.png",
        "images/result.png",
        "images/reporting.png",
    ],
    "depends" : [],
    "js" : [
        "static/src/js/jPrepend.js",
        "static/lib/ckeditor/ckeditor.js",
        "static/lib/ckeditor/adapters/jquery.js",
        "static/lib/ckeditor/config.js",
        "static/src/js/web_wysiwyg.js",
    ],
    "css" : [
        "static/src/css/web_wysiwyg.css",
    ],
    'qweb' : [
        "static/src/xml/*.xml",
    ],
    "init_xml" : [],
    "update_xml" : [],
    "demo_xml": [], 
    "test" : [],
    "auto_install" : True,
    "active" : True,
    "certificate" : "",
}
