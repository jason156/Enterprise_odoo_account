# -*- coding: utf-8 -*-
{
    'name': "IT需求管理",

    'summary': """
        IT需求管理""",

    'description': """
        manage the requirments for IT
    """,

    'author': "dtdream.com",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/dtdream_demand_app.xml',
        'workflow/dtdream_demand_app_workflow.xml',
        'views/dtdream_demand_app_js.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}