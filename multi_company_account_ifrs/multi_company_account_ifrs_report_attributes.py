# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright 2010 Eric Caudal
# License: GPL v2
#
##############################################################################


from osv import fields, osv
class res_report_attribute(osv.osv):
	_name    = "res.report.attribute"
	_description = "Reporting Attributes"
	def _default_company(self, cr, uid, context={}):
		user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
		if user.company_id:
			return user.company_id.id
		return self.pool.get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]
	_columns = {
		'type': fields.char
			( 
			'Attribute Type', 
			size=32, 
			required=True, 
			help="Attribute Type"
			),
		'code': fields.char
			( 
			'Attribute Code', 
			size=32, 
			required=True, 
			help="Attribute Code"
			),
		'name': fields.char
			( 
			'Attribute Name', 
			size=32, 
			required=True, 
			help="Attribute Name"
			),
		'sequence': fields.integer
			( 
			'Attribute Sequence', 
			required=True, 
			help="Attribute Sequence"
			),
		'company_id': fields.many2one
			(
			'res.company', 
			'Company', 
			required=True
			),
	}
	_defaults = {
		'type':       lambda *a: 'none',
		'code':       lambda *a: 'none',
		'name':       lambda *a: 'none',
		'sequence':   lambda *a: 5,
#        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr,uid,[uid],c)[0].company_id.id,
    	'company_id': lambda self, cr, uid, c: self._default_company(cr,uid,c),
    }
res_report_attribute()
