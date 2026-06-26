# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PortalInviteWizard(models.TransientModel):
    """Wizard to configure and send portal invitations."""

    _name = "portal.invite.wizard"
    _description = "Configure and Send Portal Invitations"

    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="portal_invite_wizard_partner_rel",
        string="Contacts",
        domain="[('email', '!=', False)]",
        required=True,
    )
    group_portal_id = fields.Many2one(
        comodel_name="res.groups",
        string="Portal Group",
        default=lambda self: self.env.ref("base.group_portal"),
        readonly=True,
    )
    send_email = fields.Boolean(
        string="Send Invitation Email",
        default=True,
    )
    message = fields.Text(
        string="Custom Message",
        placeholder="Add a personal note to the invitation...",
    )

    def action_invite(self):
        """Execute the portal invitation process.

        Renders the QWeb template directly via ``ir.qweb._render()`` instead
        of relying on ``mail.template.send_mail()`` to ensure all variables
        are evaluated correctly.
        """
        self.ensure_one()
        company = self.env.company
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")

        for partner in self.partner_ids.filtered("email"):
            # Ensure portal is enabled
            if not partner.portal_enabled:
                partner.sudo().write({"portal_enabled": True})

            # Ensure portal user account exists
            if not partner.user_ids or not partner.user_ids.filtered(
                lambda u: u.has_group("base.group_portal")
            ):
                partner.sudo()._create_portal_user()

            # Generate access code if needed
            if not partner.portal_code:
                partner.sudo()._generate_portal_code()

            # Send email via QWeb rendering
            if self.send_email:
                portal_link = f"{base_url}/my/home?code={partner.portal_code}"
                body_html = self.env["ir.qweb"]._render(
                    "portal_starter.portal_invite_email_body",
                    {
                        "object": partner.sudo(),
                        "company": company.sudo(),
                        "portal_link": portal_link,
                        "user": self.env.user,
                        "custom_message": self.message or "",
                    },
                )
                self.env["mail.mail"].sudo().create(
                    {
                        "subject": _("Invitation to %s Portal") % company.name,
                        "body_html": body_html,
                        "email_to": partner.email,
                        "email_from": company.email or self.env.user.email_formatted,
                    }
                ).send()

        return {"type": "ir.actions.act_window_close"}
