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
	"name" : "Multi-Company Year End Process",
	"version" : "2.0",
	"depends" : ["account", "base", "account_financial_statements"],
	"author" : "Elico Corp",
	"website" : "http://www.openerp.net.cn",
	"category" : "Finance",
	'images' : ['images/open_year.png','images/close_year.png','images/close_period.png'],
	'complexity': "normal",
	"description": """Multi-Company Enhanced Year End Process Module:
__________________________________________________________
 This module adds enhanced functionalities to the standard year-end process: 
	- Multi-Company Period Closing wizard
	- Multi-Company Fiscal Year Closing Wizard
	- Multi-Company Period Opening Wizard

==================================
DATA MODIFICATIONS
==================================
 The following field come from the account_financial_statements module (mainly for profit and loss calculation process based on level1 split):
   level1: used for the 1st level accounting classification (IFRS/US-GAAP compliant account types).
				Asset
				Liability
				Equity
				Income
				Expense
 
==================================
ADDITIONAL SET-UP
==================================

 Additional Financial Accounts setup to be done after module is implemented for correct 
 period close process (if a "net income account" is selected) :
 	- For all accounts: Set up the correct user_type (account_account_type).
	- For all accounts user_types: set up correct IFRS account type in Level 1 with the correct IFRS 
	account type (Income/Expenses/Liabilities/assets/Equities).
An example of hierarchy is given for level 1 and level 2. Those levels can be amended in the menu Account Report Attribute.  

==================================
WIZARD PROCESS SUMMARY
==================================
1.PERIOD CLOSE
This wizard allows you to close the periods within the fiscal year and transfer the result to the specified "Net earnings" account.
- Choose the company (Company must be a child of user's company) and periods.
- If a "net income account" is selected, calculates the result of the selected periods
	(IMPORTANT: based on income/expense value in level1 setup in user_type)
	and input in selected "net income account" (nothing is done if no account input).
- Change the states to 'done' for journals and periods corresponding to the selected periods.

2.PERIOD OPEN
This wizard allows you to transfer the transactions from closing fiscal year to the new fiscal year accortind to the deferral methods in account_type field.
Choose the company (Company must be a child of user's company), origin and destination fiscal years, initial period and centralized Journal where to record the transactions
and write-off information for reconciliation. The wizard then:
- Creates the new moves in the first period of new fiscal year
- Launches "reconcile" for move_line
- Updates the "End period journal" field in the closing fiscal year

3.FISCAL YEAR CLOSE
Choose the company (Company must be a child of user's company) and fiscal year to close.
Change the states to 'done' for Journals, Periods and Fiscal Year corresponding to the selected fiscal year.

==================================
ACCOUNTING CLOSING/OPENING PROCESS
==================================
O.PRELIMINARY SETUP:
	- Create a specific account type for Period end process with the following parameters:
	(Financial Management -> Configuration -> Financial accounting -> Financial Accounts)
		Name: 'Period closing'
		Code: 'closing'
		Sign: 'Positive', 
		Deferral Method: 'None',

	- For all account types, setup the account type « deferral method » to determine how the information is 
	copied from one year to another:
		1.'none': accounts for which you dont want any information to be passed to the new year
		2.'unreconciled': Accounts for which you need to transfer unreconciled information  
		3.'detail': copy all account details from the closing year to the new one.
		4.'balance': copy only the balance of previous year into new year

	- Create an account 'Opening Balance Account'  for the centralized moves:
	(Financial Management -> Configuration -> Financial accounting -> Financial Accounts)
		Name: 'Opening Balance Account'
		Code: OBA
		Parent: current chart of account
		Account Type: 'Period closing'
		Reconcile: false
		Display History: true
		Internal Type: 'Others'
	If needed, create in the same way a 'Closing Balance Account' ('CBA').

	- Create a new Journal 'Opening Balance Journal' to centralize the opening moves
	(Financial Management -> Configuration -> Financial Journals)
		Type: 'Situation', 
		View: 'Journal View', 
		Entry Sequence: 'Account Journal', 
		Default Debit Account: 'OBA Opening Balance Account', 
		Default Credit Account: 'OBA Opening Balance Account', 
		Centralized Counterpart: true
		others parameters: false
	If needed, create in the same way a 'Closing Balance Journal'.

	- Other checkings:
		1.Check that all your accounts have the correct « account type ». 
		2.Create a balance sheet summary income account ("Net Earnings - current year"). Equity account aimed 
		to sum up all net income for the year to be closed.
		3.Validate all transaction and postings (Financial/Periodical Processing/Validate account moves).

1. CLOSING ANY PERIOD PROCESS (During the Year)
When a month/quarter/year is finished and all movements of the period are accounted (cy=closing year, ny=new year):
	- Reconcile all accrual accounts for the period (accounts payable and receivable, etc.).
	- Issue the Statement of Income for the previous period.
	- BACKUP YOUR DATABASE
	- Run the 'Multi-Company Close Period Wizard' for the selected company and periods (month/quarter or year) which 
	perform the following: 
		- The income and expense account transactions for this period are summed up into a balance sheet summary income 
		account ("Net Earnings - current year", Equity Account)
		- Transaction details of income and expenses accounts are transfered to the closing journal as centralized entries 
		for the prior period.
		- Income and expense accounts balances are zeroed with regard to the period transactions and readies the accounts for 
		the start of a new monthly/quarterly period.
		- The account_journal_period and account_period table states are set to 'done' for the selected periods.
	- During the year, closing period process can be done for every period (1 every month/quarter or only once a year)

2.CLOSING FISCAL YEAR PROCESS:
	- Apply the CLOSING ANY PERIOD PROCESS for the last period/year (eg: December, 04/20cy or 12/20cy). 
	This usually occurs in the first weeks of the next fiscal period/year. 
	- Create a special adjustment period (13th) in the closing year (eg: 13/20cy) with date 31/12 and parameter 
	'Opening/closing Period' (Which allows overlapping periods).
	- Create any late-arriving transactions (after period/year-end) and any balance sheet adjustments between prior 
	year and new year deemed necessary by the accountant in a special adjustment period (13th month).  
	- When all transaction are accounted for the closing year (however many weeks/months later):
	A. PRELIMINARY STEPS:
		1.BACKUP YOUR DATABASE.
		2.Transfer the "Net Earnings - current year" account balance into 'Retained Earnings' for corporations or 'Owner Investments' 
		for Limited-Companies/Partnerships/Sole-Proprietors and this net income account then has a zero balance and can be made inactive.
		3.If the organization is a corporation and is declaring a year-end dividend then debit Retained Earnings for the 
		full amount of the dividend and credit each Shareholder account for their share of the dividend. 
		(Retained Earnings = Beginning RE + Incomes - dividend, could be negative in case of loses)
		4.Apply the CLOSING ANY PERIOD PROCESS to the adjustment sub-period (13th month). This will leave only new 
		year transaction entries in the income and expense accounts. 
		5.Official year-end Statement of Financial Position can now be generated. 
	B. OPENING THE NEW FISCAL YEAR:
		- Create a new fiscal period/year (eg: 20ny) and sub-periods and enter all new period/year transactions into the new 
		period (eg: 01~04/20ny or 01~12/20ny). 
		- Create one period (eg: 00/20ny) with date 01/01 and parameter 'Opening/closing Period' (Which allows overlapping periods).
		This period will be used to store all previous year transactions for the opening balance,
		- Run the 'Multi-Company Period Opening Wizard" for the selected fiscal year and company. The following process will be executed:
			- According to deferral method, creates new moves in the first period of new fiscal year
				1.'none': nothing done and no account information transferred from the closing period/year to the new one 
				(usually used for view and P&L accounts: expense/income)
				2.'unreconciled' : moves only « unreconciled entries » (eg: unpaid invoices) from the closing period/year to the 
				new one (usually used for receivables and payables accounts).
				3.'detail': copy all account details from the closing period/year to the new one. (eg for Equities). 
				4.'balance': create only one move in the new period/year holding the account balance of the previous one (used for 
				most of the other accounts)		
			- Launches "reconcile" for move_line
			- Updates the end_period_journal in the fiscal_year
	C. ONCE ALL INVOICES AND MOUVEMENTS ARE DONE IN PREVIOUS FISCAL YEAR, 
		Run the 'Multi-company Close Fiscal Year Wizard' for the selected fiscal year and company
		- The account_journal_period states are set to 'done' for the fiscal year.
		- The account_period table states are set to 'done' for the fiscal year.
		- The account_fiscalyear states are set to 'done' for the fiscal year.

	""",
	"init_xml" : [
	],
	"demo_xml" : [
	],
	"update_xml" : [
		"year_end_process_wizard.xml",
		"wizard/wizard_year_end_fiscalyear_close_view.xml",
		"wizard/wizard_year_end_period_close_view.xml",
		"wizard/wizard_year_end_period_open_view.xml",
	],
	"active": False,
	"installable": True
}
