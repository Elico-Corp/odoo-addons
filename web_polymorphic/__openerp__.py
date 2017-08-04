# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
 'name': 'Web Polymorphic',
 'version': '7.0.1.0.0',
 'category': 'Web',
 'depends': ['web'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
	Add a new widget named "polymorphic"
	The polymorphic field allow to dynamically store an id linked to any model in
	OpenERP instead of the usual fixed one in the view definition

	E.g:

	<field name="model" invisible="1" />
	<field name="object_id" widget="polymorphic" polymorphic="model" />
  """,
 'js': [
     'static/src/js/view_form.js'
 ],
 'installable': True,
 'application': False
 }
