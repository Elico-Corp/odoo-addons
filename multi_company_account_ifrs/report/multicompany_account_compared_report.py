##############################################################################
#
# Copyright 2010 Eric Caudal, All Rights Reserved.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from report import report_sxw
from multi_company_account_ifrs.report import multicompany_account_report
from multi_company_account_ifrs.report.multicompany_account_report import *

class multicompany_account_compared_report(multicompany_account_report):
	def __init__(self, cr, uid, name, context):
		super(multicompany_account_compared_report, self).__init__(cr, uid, name, context)
		self.context = context

	
report_sxw.report_sxw('report.multi_company_account_ifrs.multicompany.account.compared.report', 'account.account', 'addons/multi_company_account_ifrs/report/multicompany_account_compared_report.rml', parser=multicompany_account_compared_report, header=False)
