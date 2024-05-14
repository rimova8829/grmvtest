# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Hr Attendance Lunch Time',
    'version': '14.0.3.0',
    'category': 'Human Resources/Attendances',
    'author': 'Dev JS',
    'sequence': 99,
    'summary': 'Lunch Start Time And End Time  Hr Attendance',
    'depends': [
        'hr',
        'hr_attendance',
    ],
    'data': [
        'views/assets.xml',
        'views/hr_attendance.xml',
    ],
    'demo': [],
    'images': [
        'static/description/banner.png'
    ],
    'installable': True,
    'auto_install': False,
    'qweb': [
        'static/src/xml/attendance.xml',
    ],
    'application': True,
    'price': 15,
    'currency': 'EUR',
    'license': 'LGPL-3',
}
