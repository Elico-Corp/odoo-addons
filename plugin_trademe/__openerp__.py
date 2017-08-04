# -*-coding:utf-8-*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

{
    'name' : 'Trademe Plug-In',
    'version' : '7.0.1.0.0',
    'author' : 'Matiar Rahman (matiar.rahman@gmail.com)',    
    'depends' : ['sale'],
    'category': 'Generic Modules/Others',
    'description': """
This module provides the Trademe Plug-in.
=========================================
      """,
    'update_xml': ['security/trademe_security.xml',
                   'views/main.xml', 
                   'views/members.xml', 
                   'views/listing.xml', 
                   'views/questions.xml', 
                   'views/data.xml'],
    'auto_install': False,
    'installable': True,
    'active': True,
}
