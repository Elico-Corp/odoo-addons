# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{'name': 'Pos Session Customer Payment Details',
 'version': '1.0',
 'category': 'Generic Modules',
 'depends': ['point_of_sale', 'account_accountant'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
 .. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
     :alt: License

 POS Session Customer Payment Details
 ====================================

 By using our module, you can find the payment
 details for different VIP customers
 for POS in the bank statement form view and customer payment details.

 Usage
 =====
  On POS session, we have an extra lines of bank statements.

 Contributors
 ------------

 * Alex Duan: alex.duan@elico-corp.com

 .. image:: http://odoo-community.org/logo.png
    :alt: Odoo Community Association
    :target: http://odoo-community.org
""",
 'images': [],
 'demo': [],
 'data': ['view/pos_session_view.xml'],
 'installable': True,
 'application': False,
 }
