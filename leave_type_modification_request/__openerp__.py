# -*- coding: utf-8 -*-
# © 2016 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Allocation Modification Request",
    "summary": "Allocation Modification Request",
    "version": "9.0.1.0.0",
    "category": "Human Resources",
    "author": "Elico Corp",
    "website": "https://www.elico-corp.com",
    "license": "AGPL-3",
    "depends": [
        "hr_holidays",
        "website_hr",
    ],
    "data": [
        "security/allocation_modification_request_security.xml",
        "security/ir.model.access.csv",
        "views/hr_holidays_view.xml",
        "views/allocation_modification_request.xml",
    ],
    "demo": [
        "demo/allocation_modification_request_demo.xml"
    ],
    'image': [
        'static/img/step1.png',
        'static/img/step2.png',
        'static/img/step3.png',
        'static/img/step4.png',
        'static/img/step5.png',
        'static/img/step6.png',
        'static/img/step7.png',
        'static/img/step8.png',
    ],
    "installable": True,
    "auto_install": False,
}
