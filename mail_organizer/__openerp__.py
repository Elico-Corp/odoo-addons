# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
	'name': 'Mail Organizer',
	'version': '7.0.1.0.0',
	'category': 'Social Network',
	'depends': ['web_polymorphic', 'mail'],
	'author': 'Elico Corp',
	'license': 'AGPL-3',
	'website': 'https://www.elico-corp.com',
	'description': """
		This module allows you to assign a message to an existing or
		a new resource dynamically.

		You can configure the available model through
		"Settings" -> "Technical" -> "Email Organizer"

		Screencasts available at:
		https://www.youtube.com/watch?v=XYgswq6_J1I
		http://v.youku.com/v_show/id_XNjc3Njc0Nzky.html
	""",
	'images': [],
	'demo': [],
	'data': ['wizard/wizard_mail_organizer_view.xml',
	  'model_view.xml'],
	'qweb': [
	'static/src/xml/mail.xml'
	],
	'js': [
	'static/src/js/mail.js'
	],
	'css': [
	'static/src/css/mail.css'
	],
	'installable': True,
	'application': False
 }
