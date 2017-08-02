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
    "name" : "MSN Live Chat",
    "version" : "1.0",
    "category" : "Tools",
    "description" : """This module provides a Windows Live Messenger button (top right menu) to chat with the email of your choice.
    For instance, all your OpenERP users could chat with support@my-company.com (support need to have a wlm account, but can use this email through their phone, laptop, pidgin, and so on..). The users can use their wlm account or log-on as "Visitor".  
    
    To set this addon up, you will have to :
    
    - Log on your Windows Live account (http://hotmail.com/)
    - Go to this URL : http://settings.messenger.live.com/applications/WebSettings.aspx
    
    - Tick the checkbox "Allow anyone on the web to see my presence and send me messages." then click on the button "Save".
    => It's mandatory to be able to chat with you and see whether you're off-line, away, busy or available.

    - Then click on "Create HTML" on the right side menu, scrolldown to the section with the HTML code and copy your key
    => the key is the part between "invitee=" and "@apps.messenger.live.com", eg: 5853ad247d1c7d0e

    - Finally replace the two "my_own_key" in the file ~/web_wlm_chat/static/src/xml/base.xml by your own key (eg: 5853ad247d1c7d0e).
    => Now you can install the module in OpenERP.
    

    /!\ Be careful, if you don't want to copy only your key but the full code, remove the "&" otherwise you won't be able to see any views...
    """,
    "author": "Elico Corp",
    "website": "http://www.openerp.net.cn",
    "images" : [
        "images/wlm_chat.png",
        "images/support.png",
    ],
    "depends" : [],
    "qweb" : [
        "static/src/xml/base.xml",
    ],
    "init_xml" : [],
    "update_xml" : [],
    "demo_xml": [], 
    "test" : [],
    "auto_install" : False,
    "active" : True,
    "certificate" : "",
}
