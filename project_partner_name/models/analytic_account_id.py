# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):

        if not args:
            args=[]
        if context is None:
            context={}
        account_ids = []
        if name:
            account_ids = self.search(cr, uid, [('code', '=', name)] + args, limit=limit, context=context)
            if not account_ids:
                dom = []
                if '/' in name:
                    for name2 in name.split('/'):
                        # intermediate search without limit and args - could be expensive for large tables if `name` is not selective
                        account_ids = self.search(cr, uid, dom + [('name', operator, name2.strip())], limit=None, context=context)
                        if not account_ids: break
                        dom = [('parent_id','in',account_ids)]
                    if account_ids and args:
                        # final filtering according to domain (args)4
                        account_ids = self.search(cr, uid, [('id', 'in', account_ids)] + args, limit=limit, context=context)
        if not account_ids:
            return super(account_analytic_account, self).name_search(cr, uid, name, args, operator=operator, context=context, limit=limit)
        return self.name_get(cr, uid, account_ids, context=context)

    def _get_full_names(self, elmt, level):
        # a general tail recursion function
        def iter_parent_ids(elmt, level, full_names):

            if level <= 0:
                full_names.append('...')
                return (None, 0, full_names)
            elif elmt.parent_id and not elmt.type == 'template':
                full_names.append(elmt.name)
                return iter_parent_ids(elmt.parent_id, level-1, full_names)
            else:
                full_names.append(elmt.name)
                return (None, level-1, full_names)

        # call recursion function
        (_, _, full_names) = iter_parent_ids(elmt, level, [])

        return full_names

    def name_get(self, cr, uid, ids, context=None): 

        res = []
        if not ids:
            return res
        if isinstance(ids, (int, long)):
            ids = [ids]


        for id in ids:
            import pdb
            pdb.set_trace()

            elmt = self.browse(cr, uid, id, context=context)
            full_names = self._get_full_names(elmt, 6)

            if len(full_names)>0:
        
                project_ids = self.pool['project.project'].search(
                    cr, uid,
                    [('analytic_account_id', '=', id)],
                    context=context
                )


                if project_ids and (len(project_ids) > 0):
                    project_obj = self.pool['project.project'].browse(
                        cr, uid,
                        project_ids[0],
                        context=context
                    )

                    partner_ref = project_obj._get_partner_ref()[0]

                    full_names[0] = "%s - %s" % (partner_ref, full_names[0])

                # path order change to [from root to leaf]
                full_names.reverse()
                
            res.append((id, '/'.join(full_names)))

        return res


    '''    
    def _get_one_full_name(self, elmt, level=6):
        if level<=0:
            return '...'
        if elmt.parent_id and not elmt.type == 'template':
            parent_path = self._get_one_full_name(elmt.parent_id, level-1) + " / "
        else:
            parent_path = ''
        return parent_path + 'ccc' + elmt.name
    '''
