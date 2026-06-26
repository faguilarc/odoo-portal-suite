# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PortalInviteWizard(models.TransientModel):
    """Wizard to configure and send portal invitations.

    This is the form-facing wizard. The actual send logic lives in
    controllers/portal_wizard.py to keep controllers self-contained.
    """

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
        """Execute the portal invitation process."""
        self.ensure_one()
        template = self.env.ref("portal_starter.portal_invite_email_template")

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

            # Send email
            if self.send_email and template:
                template.with_context(
                    portal_link=f"/my/home?code={partner.portal_code}",
                    custom_message=self.message or "",
                ).send_mail(
                    partner.id,
                    email_values={"email_to": partner.email},
                )

        return {"type": "ir.actions.act_window_close"}
