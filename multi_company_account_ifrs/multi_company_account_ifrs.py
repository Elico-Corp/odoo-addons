# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright 2010 Eric Caudal
# License: GPL v2
#
##############################################################################


from osv import fields, osv
class account_account_type(osv.osv):
	_name    = "account.account.type"
	_inherit = "account.account.type"

	def _default_company(self, cr, uid, context={}):
		user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
		if user.company_id:
			return user.company_id.id
		return self.pool.get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]

	_columns = {
        'level1': fields.many2one
            (
			'res.report.attribute',
			'Level 1',
#			required=True,
			help="First level account category (based on the five standard IFRS/US-GAAP account types). Those categories are used in multi-company IFRS reports. N/A if not appliable"
			),
        'level2': fields.many2one
            (
			'res.report.attribute',
			'Level 2',
#			required=True,
			help="Second level account category (based on IFRS). Those categories are used for totals in multi-company IFRS reports. N/A if not appliable"
			),

		'current': fields.boolean
			(
			'Current',
			required=True,
			help="Select whether this account is current or long-term (aka non-current). A 'current' account means it applies to the current fiscal year."
			),
		'operating': fields.boolean
			(
			'Operating', 
			required=True, 
			help="Select whether this account is operating or non-operating. An 'operating' account means it applies to core operations of the company.  Otherwise, 'non-operating' means it applies to non-core operations."
			),
		'company_id': fields.many2one
			(
			'res.company', 
			'Company', 
			required=True
			),
	}

	_defaults = {
	'current':    lambda *a: True,
	'operating':  lambda *a: True,
#	'level1':     lambda self, cr, uid, context : self.pool.get('res.report.attribute').search(cr, uid, [('code', '=', 'na_l1')])[0],
#	'level2':     lambda self, cr, uid, context : self.pool.get('res.report.attribute').search(cr, uid, [('code', '=', 'na_l2')])[0],
#	'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr,uid,[uid],c)[0].company_id.id,
	'company_id': lambda self, cr, uid, c: self._default_company(cr,uid,c),
	}

account_account_type()

