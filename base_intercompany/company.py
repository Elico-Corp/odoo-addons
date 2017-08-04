# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import orm, fields


class res_intercompany(orm.Model):
    _name = 'res.intercompany'
    _description = 'Inter-Company'

    def _select_concepts(self, cr, uid, context=None):
        """ Available concepts

        Can be inherited to add custom versions.
        """
        return []

    def _select_models(self, cr, uid, context=None):
        """ Available Object names

        Can be inherited to add custom versions.
        """
        return {}

    def _get_model(self, cr, uid, ids, name, arg, context=None):
        """ Available versions

        Can be inherited to add custom versions.
        """
        res = {}
        for intercompany in self.browse(cr, uid, ids, context):
            model = None
            if intercompany.concept:
                model = self._select_models(
                    cr, uid)[intercompany.concept]
            res[intercompany.id] = model
        return res

    def get_intercompany(self, cr, uid, obj_id,
                         obj_class_name, obj_name, context=None):
        """
        get company from and to
        """
        if isinstance(obj_id, list):
            obj_id = obj_id[0]
        assert isinstance(obj_id, int) or isinstance(obj_id, long)
        obj = self.pool.get(obj_class_name).browse(
            cr,
            uid,
            obj_id,
            context=None)
        company = obj.company_id
        ic_uid_ids = None
        company_to_ids = []
        for ic in company.intercompany_ids:
            if ic.concept == obj_name:
                company_to_ids.append(ic.company_to.id)
                ic_uid_ids = ic.icops_uid.id
        if company.intercompany_ids:
            ic_uid_ids = company.intercompany_ids[0].icops_uid.id
        return obj.company_id.id, company_to_ids, ic_uid_ids

    def _check_intercompany_user(self, cr, uid, ids, context=None):
        for ic in self.browse(cr, uid, ids, context=context):
            if not ic.icops_uid:
                return False
        return True

    _columns = {
        'backend_id': fields.many2one('icops.backend', 'Original Backend',
                                      required=True, ondelete='cascade'),
        'backend_to': fields.many2one('icops.backend', 'Destination Backend',
                                      required=True, ondelete='cascade'),
        'concept': fields.selection(_select_concepts, string="Concept",
                                    required=True),
        'model': fields.function(_get_model, type='char',
                                 string='Object', store=False),
        'icops_uid': fields.related(
            'backend_to', 'icops_uid', type='many2one',
            relation='res.users', readonly=True, string='IC User'),
        'on_create': fields.boolean('Create'),
        'on_write': fields.boolean('Update'),
        'on_unlink': fields.boolean('Delete'),
        'on_confirm': fields.boolean('Confirm'),
        'on_cancel': fields.boolean('Cancel')
    }

    _constraints = [
        (_check_intercompany_user, 'Please set IC user for the Company first',
            ['icops_uid'])
    ]

    _defaults = {
        'backend_id': lambda self, cr, uid, c: c.get('active_id', False),
    }
    # _sql_constraints = [(
    #     'company_from_company_to_unique', 'unique(company_from, company_to)',
    #     'A setup for that company already exists')]

    def check_need_create_intercompany_object(
            self, cr, uid, company_from, company_to, concept,
            event, return_list_type=False, regular=False):
        """ @company_from
            @company_to
            @o2o_field_name  file name.Example, so2po po2so ,,,,
            @node  value of  o2o_field_name ,  draft, confirm
            @return_list_type,  the return type is list or boolean
        """

        if type(company_to) != list:
            company_to = [company_to]
        request = [('company_from', '=', company_from),
                   ('concept', '=', concept),
                   (event, '=', True)]
        if not regular:
            request.append(('company_to', 'in', company_to))
        intercompany_ids = self.search(
            cr, uid, request)
        if return_list_type:
            return intercompany_ids
        else:
            return intercompany_ids and True or False
