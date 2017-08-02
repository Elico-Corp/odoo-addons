# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (c) 2010-2011 Elico Corp. All Rights Reserved.
#    Author:            Eric CAUDAL <contact@elico-corp.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
	"name" : "Multi-Company Financial Statements Module",
	"version" : "2.0",
	"depends" : ["account", "base"],
	"author" : "Eric Caudal (contact@elico-corp.com)",
	"description": """Multi-Company Financial Statements Module:
__________________________________________________________
 This module adds the the following functionalities: 
	- Multi-Company Income Statement (with IFRS breakdown)
	- Multi-Company Statement Of Financial Position (with IFRS breakdown)

==================================
DATA MODIFICATIONS
==================================
 The following fields have been added to account_account_type table:
   level1: used for the 1st level accounting classification (IFRS/US-GAAP compliant account types).
				Asset
				Liability
				Equity
				Income
				Expense
   level2: 2nd level accounting classification (necessary mostly for Gross Profit report in Income Statement report) .
			 	Receivable
			 	Cash
			 	Inventory
			 	Other Current Assets
			 	Lands and Properties
			 	Accumulated Depreciations
			 	Intangible Assets
			 	Other Assets
			 	Payable
			 	Tax Payable
			 	Other Current Liabilities 
			 	Equities
   current:   this boolean is used to indicate current/non-current account status.
				current:     has impact only in current year.
				non-current: has impact even beyond current year.
   operating: this boolean is used to indicate operating/non-operating account status.
				operating:      related to core operations of the company.
				non-operating:  not related to core operations of the company.
   sequence: sorting field
 
==================================
ADDITIONAL SET-UP
==================================
Additional Financial Accounts setup to be done after module is implemented for correct reports.
ACCOUNT TYPE
	- Set up 'current' (default: True) flags for account only within the current period.
	- Set up 'operating' (default: True) flags for account concerning usual company operations.
	- Set up level 1 for correct IFRS account type split (Income/Expenses/Liabilities/assets/Equities).
	- Set up level2 attributes if more split details are required.
ACCOUNTS
	- Set up the correct user_type (account_account_type).
PLEASE NOTE:
	- For Income Statement : the level2 attribute is used to calculate cumulative totals based on sequence numbers
	- Signs on the reports are calculated based on the report_type field ("P&L / BS Category")
	- An example of hierarchy is given for level 1 and level 2. Those levels can be amended in the menu Account Report Attribute.  

==================================
MULTI-COMPANY REPORTING WIZARD PROCESS SUMMARY
==================================
- Choose the company and the periods for the report (Company must be a child of user's company)
- Allow to compare 2 periods.
- Allow to choose 5 custom levels for breakdown (level 1, level 2, user_type, operating and current)
- Allow to create reports with/without cumulative totals (needed anyway for Gross Profit report)

==================================
TO BE DONE 
==================================
- Create a report allowing to print a Income Statement of a closed period based on the closing journal of a period.
- Create multi-company Accounting Budget and incorporate to reporting. 

==================================
KNOWN BUG 
==================================
First Data loading is incorrect and must corrected through OpoenERP client or PGAdmin: 
- the parent company is assigned by default instead of the user's company
- the existing user_type level 1 and level 2 are left without default value

==================================
UNINSTALL 
==================================
Uninstall process can fail if some imported user_type are still assigned to accounts when the uninstall process is launch: 
so first change the user_type to a new value and launch uninstall process.
 
	""",
	"website" : "http://www.openerp.net.cn",
	"category" : "Multi-company/Accounting",
	"init_xml" : [
	],
	"demo_xml" : [
	],
	"update_xml" : [
		"elico_multi_company_financial_statements_view.xml",
		"elico_multi_company_financial_statements_report.xml",
		"data/elico_multi_company_financial_statements_report_attribute.xml",
		"data/elico_multi_company_financial_statements_account_type.xml",
		"security/multi_company_security.xml",
        	"security/ir.model.access.csv",
        	"wizard/wizard_multicompany_report_view.xml",
	],
	"active": False,
	"installable": True
}
