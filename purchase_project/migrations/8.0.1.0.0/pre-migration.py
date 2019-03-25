# -*- coding: utf-8 -*-
from openerp.openupgrade import openupgrade

xmlid_renames = [
    ('project.project_purchase_form_view', 'project.edit_project'),
    ('project.projects_purchase_kanban_view',
     'project.projects_purchase_kanban'),
    ('purchase.purchase_order_form_view_inherit',
     'purchase.purchase_order_form'),
    ('purchase.purchase_order_tree_view_inherit',
     'purchase.purchase_order_tree'),
    ('purchase.purchase_order_search_view_inherit',
     'purchase.view_purchase_order_filter'),
]


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_xmlids(cr, xmlid_renames)
