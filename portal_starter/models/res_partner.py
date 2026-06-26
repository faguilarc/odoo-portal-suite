# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    """Extend res.partner with portal-specific fields."""
    _inherit = "res.partner"

    portal_enabled = fields.Boolean(
        string="Portal Access Enabled",
        default=False,
        help="Enable portal access for this contact",
    )
    portal_code = fields.Char(
        string="Portal Access Code",
        copy=False,
        readonly=True,
        help="Unique code used for portal authentication links",
    )
    portal_max_sessions = fields.Integer(
        string="Max Concurrent Sessions",
        default=3,
        help="Maximum number of concurrent portal sessions allowed",
    )
    portal_last_login = fields.Datetime(
        string="Last Portal Login",
        readonly=True,
    )
    portal_login_count = fields.Integer(
        string="Portal Login Count",
        default=0,
    )
    portal_allowed_document_types = fields.Many2many(
        comodel_name="portal.document.type",
        relation="partner_document_type_rel",
        string="Allowed Document Types",
        help="Document types this partner can access through the portal",
    )
    portal_theme = fields.Selection(
        selection=[
            ("default", "Default Theme"),
            ("modern", "Modern Theme"),
            ("classic", "Classic Theme"),
            ("dark", "Dark Theme"),
        ],
        string="Portal Theme",
        default="default",
        help="Visual theme for this partner's portal experience",
    )
    portal_custom_css = fields.Text(
        string="Custom Portal CSS",
        help="Additional CSS for this partner's portal (advanced)",
    )
    portal_company_logo = fields.Binary(
        string="Portal Logo Override",
        help="Override the default company logo in the portal for this partner",
    )
    portal_sidebar_items = fields.Json(
        string="Sidebar Configuration",
        default=lambda self: self._default_sidebar_items(),
        help="JSON configuration for portal sidebar menu items",
    )

    @api.model
    def _default_sidebar_items(self):
        """Return default sidebar configuration."""
        return [
            {"id": "orders", "label": "My Orders", "icon": "fa-shopping-cart", "sequence": 1},
            {"id": "invoices", "label": "Invoices", "icon": "fa-file-invoice-dollar", "sequence": 2},
            {"id": "quotes", "label": "Quotes", "icon": "fa-file-alt", "sequence": 3},
            {"id": "deliveries", "label": "Deliveries", "icon": "fa-truck", "sequence": 4},
            {"id": "support", "label": "Support Tickets", "icon": "fa-headset", "sequence": 5},
            {"id": "profile", "label": "My Profile", "icon": "fa-user", "sequence": 6},
        ]

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-generate portal_code on partner creation."""
        records = super().create(vals_list)
        for record in records:
            if record.portal_enabled and not record.portal_code:
                record._generate_portal_code()
        return records

    def write(self, vals):
        """Generate portal code when portal is enabled."""
        result = super().write(vals)
        if vals.get("portal_enabled"):
            for record in self:
                if record.portal_enabled and not record.portal_code:
                    record._generate_portal_code()
        return result

    def _generate_portal_code(self):
        """Generate a unique portal access code."""
        self.ensure_one()
        self.portal_code = self.env["ir.sequence"].next_by_code(
            "portal.starter.code"
        ) or self.env["ir.sequence"].sudo().create(
            {
                "name": "Portal Access Code Sequence",
                "code": "portal.starter.code",
                "prefix": "PRT-",
                "padding": 8,
            }
        ).next_by_code("portal.starter.code")

    def action_open_portal(self):
        """Open the portal URL for this partner."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": f"/my/home?partner_id={self.id}",
            "target": "new",
        }

    def action_send_portal_invite(self):
        """Send a portal invitation email to this partner.

        Renders the QWeb template ``portal_starter.portal_invite_email_body``
        with explicit variables (object, company, portal_link) and creates a
        ``mail.mail`` record that is sent immediately.
        """
        self.ensure_one()
        if not self.email:
            raise ValidationError(_("Partner must have an email to receive portal invitation."))

        self._generate_portal_code()

        company = self.company_id or self.env.company
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        portal_link = f"{base_url}/my/home?code={self.portal_code}"

        # Render the QWeb view — NOT through mail.template.send_mail()
        body_html = self.env["ir.qweb"]._render(
            "portal_starter.portal_invite_email_body",
            {
                "object": self.sudo(),
                "company": company.sudo(),
                "portal_link": portal_link,
                "user": self.env.user,
                "custom_message": "",
            },
        )

        self.env["mail.mail"].sudo().create(
            {
                "subject": _("Invitation to %s Portal") % company.name,
                "body_html": body_html,
                "email_to": self.email,
                "email_from": company.email or self.env.user.email_formatted,
            }
        ).send()
