# -*- coding: utf-8 -*-
from openerp.openupgrade import openupgrade

xmlid_renames = [
    ('crm.opportunities_form_view', 'crm.crm_case_form_view_oppor'),
    ('crm.opportunities_kanban_view', 'crm.crm_case_kanban_view_leads'),
    ('project.project_opportunity_form_view', 'project.edit_project'),
    ('project.project_opportunity_tree_view', 'project.view_project'),
    ('project.project_form_view,', 'project.edit_project'),
    ('project.projects_kanban_view_inherit,', 'project.view_project_kanban'),
    ('project.project_search_view,', 'project.view_project_project_filter'),
    ('sale.sale_order_form_view,', 'sale.view_order_form'),
    ('sale.sale_order_search_view,', 'sale.view_sales_order_filter'),
]


column_renames = {
    'crm_lead': [
        ('project_line', 'project_line_ids'),
    ],
}


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_xmlids(cr, xmlid_renames)
    openupgrade.rename_columns(cr, column_renames)
