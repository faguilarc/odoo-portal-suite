# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PortalDocumentType(models.Model):
    """Document types that can be exposed through the portal."""
    _name = "portal.document.type"
    _description = "Portal Document Type"
    _order = "sequence, name"
    _rec_name = "name"

    name = fields.Char(
        string="Name",
        required=True,
        translate=True,
    )
    code = fields.Char(
        string="Technical Code",
        required=True,
        help="Unique identifier used in code (e.g. 'sale_order', 'account_invoice')",
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Odoo Model",
        required=True,
        ondelete="cascade",
        help="The Odoo model this document type represents",
    )
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    icon = fields.Char(
        string="Icon Class",
        default="fa-file",
        help="Font Awesome icon class (e.g. fa-file, fa-shopping-cart)",
    )
    color = fields.Char(
        string="Color",
        default="#3498db",
        help="Hex color code for the document type badge",
    )
    description = fields.Text(
        translate=True,
        help="Description shown to portal users",
    )
    portal_visible = fields.Boolean(
        string="Visible in Portal",
        default=True,
    )
    max_items_per_page = fields.Integer(
        string="Items Per Page",
        default=20,
    )
    allowed_actions = fields.Json(
        string="Allowed Actions",
        default=lambda self: self._default_allowed_actions(),
        help="JSON list of actions portal users can perform on this document type",
    )
    field_ids = fields.Many2many(
        comodel_name="ir.model.fields",
        relation="portal_doc_type_field_rel",
        string="Visible Fields",
        domain="[('model_id', '=', model_id)]",
        help="Fields visible to portal users for this document type",
    )

    @api.model
    def _default_allowed_actions(self):
        """Return default allowed actions for a document type."""
        return ["view", "download_pdf"]

    def name_get(self):
        """Display name with code."""
        result = []
        for record in self:
            result.append((record.id, f"{record.name} ({record.code})"))
        return result


class PortalConfig(models.Model):
    """Global portal configuration settings."""
    _name = "portal.config"
    _description = "Portal Configuration"
    _rec_name = "company_id"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )
    portal_name = fields.Char(
        string="Portal Name",
        default="My Portal",
        help="Name displayed in the portal header",
    )
    portal_welcome_message = fields.Html(
        string="Welcome Message",
        help="HTML message shown on the portal home page",
        default="<h2>Welcome to your portal</h2><p>Here you can manage your documents and account information.</p>",
    )
    portal_show_company_logo = fields.Boolean(
        string="Show Company Logo",
        default=True,
    )
    portal_favicon = fields.Binary(
        string="Custom Favicon",
    )
    primary_color = fields.Char(
        string="Primary Color",
        default="#1C6EF2",
    )
    secondary_color = fields.Char(
        string="Secondary Color",
        default="#6C757D",
    )
    enable_document_download = fields.Boolean(
        string="Enable Document Download",
        default=True,
    )
    enable_online_payment = fields.Boolean(
        string="Enable Online Payment",
        default=False,
        help="Allow customers to pay invoices through the portal",
    )
    enable_ticket_system = fields.Boolean(
        string="Enable Support Tickets",
        default=True,
    )
    enable_notifications = fields.Boolean(
        string="Enable Notifications",
        default=True,
    )
    notification_email = fields.Boolean(
        string="Email Notifications",
        default=True,
    )
    notification_in_app = fields.Boolean(
        string="In-App Notifications",
        default=True,
    )
    session_timeout_minutes = fields.Integer(
        string="Session Timeout (minutes)",
        default=480,
        help="Portal session inactivity timeout in minutes",
    )
    max_login_attempts = fields.Integer(
        string="Max Login Attempts",
        default=5,
    )
    lockout_minutes = fields.Integer(
        string="Lockout Duration (minutes)",
        default=30,
        help="Account lockout duration after max login attempts",
    )
    enable_two_factor = fields.Boolean(
        string="Enable Two-Factor Authentication",
        default=False,
    )
    footer_text = fields.Char(
        string="Footer Text",
        default="Powered by Odoo",
    )
    show_social_links = fields.Boolean(
        string="Show Social Links",
        default=False,
    )
    social_facebook = fields.Char(string="Facebook URL")
    social_linkedin = fields.Char(string="LinkedIn URL")
    social_twitter = fields.Char(string="X (Twitter) URL")
    social_instagram = fields.Char(string="Instagram URL")
    custom_css = fields.Text(
        string="Global Custom CSS",
        help="Additional CSS applied to the entire portal",
    )
    custom_js = fields.Text(
        string="Global Custom JS",
        help="Additional JavaScript applied to the entire portal",
    )

    _sql_constraints = [
        ("company_uniq", "UNIQUE(company_id)", "Only one portal config per company is allowed."),
    ]

    @api.onchange("primary_color")
    def _onchange_primary_color(self):
        """Auto-generate a complementary secondary color."""
        if self.primary_color:
            self.secondary_color = self._complementary_color(self.primary_color)

    def _complementary_color(self, hex_color):
        """Generate a lighter complementary color from a hex color."""
        try:
            hex_color = hex_color.lstrip("#")
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            r = min(255, r + 80)
            g = min(255, g + 80)
            b = min(255, b + 80)
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return "#6C757D"

    def action_open_portal_preview(self):
        """Open a preview of the portal."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": "/my/home?preview=true",
            "target": "new",
        }

    def action_open_portal_config(self):
        config = self.env["portal.config"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )
        if not config:
            config = config.create({"company_id": self.env.company.id})
        return {
            "type": "ir.actions.act_window",
            "name": "Portal Configuration",
            "res_model": "portal.config",
            "res_id": config.id,  # ← acá está la clave
            "view_mode": "form",
        }
