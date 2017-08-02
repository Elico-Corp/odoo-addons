{
	"name" : "Multi-Company IFRS Accounting Module",
	"version" : "1.1",
	"depends" : ["account", "base", "multi_company", "multi_company_account"],
	"author" : "Eric Caudal",
	"description": """Multi-Company Financial and Accounting Module:
__________________________________________________________
 This module adds the the following functionalities to the multi-company and standard modules: 
	- Multi-Company Period Closing wizard
	- Multi-Company Fiscal Year Closing Wizard
	- Multi-Company Period Opening Wizard
	- Multi-Company Statement of Income (with IFRS breakdown)
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

 Security rules added for account_type for company_id restrictions
 
==================================
ADDITIONAL SET-UP
==================================

 Additional Financial Accounts setup to be done after module is implemented for correct reports and 
 period close process (if a "net income account" is selected) :
	- For all accounts types: Set up 'current' (default: True) and 'operating' (default: True) flags.
 	- For all accounts: Set up the correct user_type (account_account_type).
	- For all accounts user_types: set up correct IFRS account type in Level 1 with the correct IFRS 
	account type (Income/Expenses/Liabilities/assets/Equities).
	- For Statement of Financial position accounts: select the desired level2 attributes.
	- For Income Statement accounts types and Income Statement : select the 2nd level attribute as totals 
	(To get the proper calculation of the cumulative totals for the gross profit, the sequence numbers must be accurate).
An example of hierarchy is given for level 1 and level 2. Those levels can be amended in the menu Account Report Attribute.  

==================================
WIZARD PROCESS SUMMARY
==================================
1.FISCAL YEAR CLOSE
- Choose the company (Company must be a child of user's company) and fiscal year to close.
- It launches 3 SQL statements to set state 'done' to Journal, period and fiscal year for the selected fiscal year.

2.PERIOD CLOSE
- Choose the company (Company must be a child of user's company) and periods.
- If a "net income account" is selected, calculates the result of the selected periods 
	(IMPORTANT: based on income/expense value in account_type_level1)
	and input in selected "net income account" (nothing is done if no account input).
- Launches 2 SQL statements to set state 'done' to selected journals and periods.

3.PERIOD OPEN
- Choose the company (Company must be a child of user's company), periods to be opened and closed, opening journal 
	and write-off information for reconciliation.
- According to deferral method, creates new moves in the first period of new fiscal year
- Launches "reconcile" for move_line
- Updates the end_period_journal in the fiscal_year

4.MULTI-COMPANY REPORTING
- Choose the company and the periods for the report (Company must be a child of user's company)
- Allow to compare 2 periods.
- Allow to choose 5 custom levels for breakdown (level 1, level 2, user_type, operating and current)
- Allow to create reports with/without cumulative totals (needed for Gross Profit report)

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
		Parent: none
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
		2.Create a balance sheet summary income account (Net Income - 20cy[closing year]). Equity account aimed 
		to sum up all net income for the year to be closed.
		3.Validate all transaction and postings (Financial/Periodical Processing/Validate account moves).

1. CLOSING ANY PERIOD PROCESS (During the Year)
When a month/quarter/year is finished and all movements of the period are accounted (cy=closing year, ny=new year):
	- Reconcile all accrual accounts for the period (accounts payable and receivable, etc.).
	- Issue the Statement of Income for the previous period.
	- Make a backup of your database. 
	- Run the 'Multi-Company Close Period Wizard' for the selected company and periods (month/quarter or year) which 
	perform the following: 
		- The income and expense account transactions for this period are summed up into a balance sheet summary income 
		account (« Net Income - 20cy », Equity Account)
		- Transaction details of income and expenses accounts are transfered to the closing journal as centralized entries 
		for the prior period.
		- Income and expense accounts balances are zeroed with regard to the period transactions and readies the accounts for 
		the start of a new monthly/quarterly period.
		- The account_journal_period and account_period table states are set to 'done' for the selected periods.
	- During the year, as many closing period process can be done (1 every month/quarter or only once a year)

2.CLOSING FISCAL YEAR PROCESS:
	- Apply the CLOSING ANY PERIOD PROCESS for the last period/year (eg: December, 04/20cy or 12/20cy). 
	This usually occurs in the first weeks of the next fiscal period/year. 
	- Create a special adjustment period (13th) in the closing year (eg: 13/20cy) with date 31/12 and parameter 
	'Opening/closing Period' (Which allows overlapping periods).
	- Create any late-arriving transactions (after period/year-end) and any balance sheet adjustments between prior 
	year and new year deemed necessary by the accountant in a special adjustment period (13th month).  
	- When all transaction are accounted for the closing year (however many weeks/months later):
	A. Preliminary steps:
		1.Make a backup of the database
		2.Transfer the 'Net Income - 20cy' account balance into 'Retained Earnings' for corporations or 'Owner Investments' 
		for Limited-Companies/Partnerships/Sole-Proprietors and this net income account then has a zero balance and can be made inactive.
		3.If the organization is a corporation and is declaring a year-end dividend then debit Retained Earnings for the 
		full amount of the dividend and credit each Shareholder account for their share of the dividend. 
		(Retained Earnings = Beginning RE + Incomes ￢ﾀﾓ dividend, could be negative in case of loses)
		4.Apply the CLOSING ANY PERIOD PROCESS to the previous adjustment sub-period (13th month). This will leave only new 
		year transaction entries in the income and expense accounts. 
		5.Official year-end statement of financial position and Statement of Income can now be generated. 
		6.Create a new 'Net Income -20ny[new year]' account (not necessary at that step but need for 1st period closing).
	B. Opening the new fiscal year :
		- Create a new fiscal period/year (eg: 20ny) and sub-periods and enter all new period/year transactions into the new 
		period (eg: 01~04/20ny or 01~12/20ny). 
		- Create one period (eg: 00/20ny) with date 01/01 and parameter 'Opening/closing Period' (Which allows overlapping periods).
		This period will be used to store all transactions for the opening balance, (calculated from the previous period balance) 
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
		(all invoices must be paid in the fiscal year before closing).
		- The account_journal_period states are set to 'done' for the fiscal year.
		- The account_period table states are set to 'done' for the fiscal year.
		- The account_fiscalyear states are set to 'done' for the fiscal year.
	

	""",
	"website" : "",
	"category" : "Multi-company/Accounting",
	"init_xml" : [
	],
	"demo_xml" : [
	],
	"update_xml" : [
		"multi_company_account_ifrs_view.xml",
		"multi_company_account_ifrs_wizard.xml",
		"multi_company_account_ifrs_report.xml",
		"data/multicompany_report_attribute.xml",
		"data/multicompany_account_type.xml",
		"security/multicompany_security.xml",
        "security/ir.model.access.csv",
	],
#	"translations" : {
#		"fr": "i18n/french_fr.csv"
#	},
	"active": False,
	"installable": True
}
