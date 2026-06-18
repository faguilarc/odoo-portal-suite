# -*- coding: utf-8 -*-
{
    "name": "Portal Starter Kit",
    "summary": "Base toolkit for building custom customer/vendor portals on Odoo 17 Community",
    "version": "17.0.1.0.0",
    "category": "Portal",
    "author": "faguilarc",
    "website": "https://github.com/faguilarc/odoo-portal-suite",
    "license": "LGPL-3",
    "depends": [
        "base",
        "portal",
        "web",
        "mail",
    ],
    "data": [
        "security/portal_starter_security.xml",
        "security/ir.model.access.csv",
        "data/portal_starter_data.xml",
        "views/res_partner_views.xml",
        "views/portal_templates.xml",
        "views/portal_home_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "portal_starter/static/src/css/portal_starter.css",
            "portal_starter/static/src/js/portal_starter.js",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}