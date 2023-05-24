# -*- coding: utf-8 -*-
{
    'name': "Picking Labels",
    'summary': "Picking Labels",
    'description': """QA picking labels""",

    'author': "FIXDOO SOLUTIONS",
    'category': 'Stock',
    'version': '1.0',
    'application': True,
    'website': '',
    # any module necessary for this one to work correctly
    'depends': ['stock'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/label_template.xml',
        'data/stowage_label_template.xml',
        'data/single_label_template.xml',
        'views/wizard_stock_labels.xml'
    ],
    'qweb': [],
    'demo': [],
    'license': '',
}
