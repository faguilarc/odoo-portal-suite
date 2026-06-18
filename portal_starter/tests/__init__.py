# -*- coding: utf-8 -*-
from odoo.tests import HttpCase, tagged


class TestPortalStarter(HttpCase):
    """Test portal starter module functionality."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.partner_demo")

    def test_portal_config_created(self):
        """Test that default portal config is created on install."""
        config = self.env["portal.config"].search(
            [("company_id", "=", self.env.company.id)]
        )
        self.assertTrue(len(config) == 1, "Default portal config should exist")

    def test_document_types_created(self):
        """Test that default document types are created."""
        doc_types = self.env["portal.document.type"].search([])
        self.assertTrue(
            len(doc_types) >= 3,
            "At least 3 document types should be created by default",
        )

    def test_portal_code_generation(self):
        """Test portal access code generation."""
        self.partner.write({"portal_enabled": True})
        self.partner._generate_portal_code()
        self.assertTrue(
            self.partner.portal_code, "Portal code should be generated"
        )
        self.assertTrue(
            self.partner.portal_code.startswith("PRT-"),
            "Portal code should start with PRT-",
        )

    def test_portal_home_page(self):
        """Test portal home page loads correctly."""
        self.env.ref("base.group_portal").users[0].partner_id.write({
            "portal_enabled": True,
        })
        res = self.url_open("/my/home")
        self.assertEqual(res.status_code, 200)

    def test_sidebar_default_items(self):
        """Test default sidebar items are generated."""
        items = self.partner._default_sidebar_items()
        self.assertTrue(len(items) >= 5, "Default sidebar should have 5+ items")
        self.assertEqual(items[0]["id"], "orders")