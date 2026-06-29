# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, content_disposition
from odoo.addons.portal.controllers.portal import CustomerPortal


class PortalStarterController(CustomerPortal):
    """Extended portal controller with custom home and document listing."""

    def _prepare_home_values(self, values):
        """Add portal config and document types to home page values."""
        # values = super()._prepare_home_values(values)
        partner = request.env.user.partner_id.sudo()

        portal_config = request.env["portal.config"].sudo().search(
            [("company_id", "=", request.env.company.id)],
            limit=1,
        )

        document_types = (
            request.env["portal.document.type"]
            .sudo()
            .search([
                ("portal_visible", "=", True),
                ("id", "in", partner.portal_allowed_document_types.ids),
            ])
            if partner.portal_allowed_document_types
            else request.env["portal.document.type"].sudo().search([
                ("portal_visible", "=", True),
            ])
        )

        sidebar_items = partner.portal_sidebar_items or []

        values.update({
            "portal_config": portal_config,
            "document_types": document_types,
            "sidebar_items": sidebar_items,
            "page_name": "home",
        })
        return values

    # ------------------------------------------------------------------
    # Override the default /my route so portal users land on our custom
    # home instead of the stock Odoo portal.
    # ------------------------------------------------------------------
    @http.route(
        ["/my", "/my/home"],
        type="http",
        auth="user",
        website=True,
    )
    def home(self, **kw):
        """Render the custom Portal Starter home page.

        Overrides ``CustomerPortal.home`` so that /my (the default
        landing page for portal users) shows our branded portal with
        the welcome banner, document-type cards and theme from
        ``portal.config``.
        """
        values = self._prepare_home_values({})
        partner = request.env.user.partner_id.sudo()

        if partner.portal_theme and partner.portal_theme != "default":
            values["portal_theme"] = partner.portal_theme

        if partner.portal_custom_css:
            values["partner_custom_css"] = partner.portal_custom_css

        return request.render("portal_starter.portal_home_page", values)

    @http.route(
        ["/my/documents/<string:doc_type>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_document_list(
        self, doc_type=None, search="", search_in="all", page=1, sortby=None, **kw
    ):
        """List documents of a specific type in the portal."""
        doc_type_record = (
            request.env["portal.document.type"]
            .sudo()
            .search(
                [("code", "=", doc_type), ("portal_visible", "=", True)],
                limit=1,
            )
        )
        if not doc_type_record:
            return request.sudo().not_found()

        partner = request.env.user.partner_id.sudo()
        model = doc_type_record.model_id.model

        domain = self._get_document_domain(model, partner, search, search_in)

        sortby_mapping = {
            "date_desc": {"name": "create_date", "order": "desc"},
            "date_asc": {"name": "create_date", "order": "asc"},
            "name_asc": {"name": "name", "order": "asc"},
            "name_desc": {"name": "name", "order": "desc"},
            "amount_desc": {"name": "amount_total", "order": "desc"},
            "amount_asc": {"name": "amount_total", "order": "asc"},
        }
        if not sortby:
            sortby = "date_desc"
        sort_config = sortby_mapping.get(sortby, sortby_mapping["date_desc"])

        items_per_page = doc_type_record.max_items_per_page or 20
        document_model = request.env[model].sudo()
        total_count = document_model.search_count(domain)

        # Build pager via the website model — works even if
        # request.website is not set by the routing layer.
        website = request.env["website"].sudo().get_current_website()
        pager = website.pager(
            url=f"/my/documents/{doc_type}",
            total=total_count,
            page=page,
            step=items_per_page,
        )
        documents = document_model.search(
            domain,
            limit=items_per_page,
            offset=pager["offset"],
            order=f"{sort_config['name']} {sort_config['order']}",
        )

        values = self._prepare_home_values({
            "doc_type": doc_type_record,
            "documents": documents,
            "pager": pager,
            "search": search,
            "search_in": search_in,
            "sortby": sortby,
            "page_name": "documents",
        })
        return request.render("portal_starter.portal_document_list_page", values)

    @http.route(
        ["/my/documents/<string:doc_type>/<int:doc_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_document_detail(self, doc_type=None, doc_id=None, **kw):
        """Show document detail page in the portal."""
        doc_type_record = (
            request.env["portal.document.type"]
            .sudo()
            .search(
                [("code", "=", doc_type), ("portal_visible", "=", True)],
                limit=1,
            )
        )
        if not doc_type_record:
            return request.not_found()

        model = doc_type_record.model_id.model
        partner = request.env.user.partner_id.sudo()

        domain = self._get_document_domain(model, partner)
        domain.append(("id", "=", doc_id))
        document = request.env[model].sudo().search(domain, limit=1)
        if not document:
            return request.not_found()

        values = self._prepare_home_values({
            "doc_type": doc_type_record,
            "document": document,
            "page_name": "document_detail",
        })
        return request.render("portal_starter.portal_document_detail_page", values)

    @http.route(
        ["/my/documents/<string:doc_type>/<int:doc_id>/download"],
        type="http",
        auth="user",
    )
    def portal_document_download(self, doc_type=None, doc_id=None, **kw):
        """Download a document as PDF from the portal."""
        doc_type_record = (
            request.env["portal.document.type"]
            .sudo()
            .search(
                [("code", "=", doc_type), ("portal_visible", "=", True)],
                limit=1,
            )
        )
        if not doc_type_record:
            return request.not_found()

        model = doc_type_record.model_id.model
        partner = request.env.user.partner_id.sudo()
        domain = self._get_document_domain(model, partner)
        domain.append(("id", "=", doc_id))
        document = request.env[model].sudo().search(domain, limit=1)
        if not document:
            return request.not_found()

        # Try to find and render a PDF report
        report = (
            request.env["ir.actions.report"]
            .sudo()
            .search(
                [("model", "=", model), ("report_type", "=", "qweb-pdf")],
                limit=1,
            )
        )
        if report:
            pdf_content, _ = report.with_context({}).sudo()._render_qweb_pdf([doc_id])
            pdfhttpheaders = [
                ("Content-Type", "application/pdf"),
                (
                    "Content-Disposition",
                    content_disposition(f"{doc_type}_{doc_id}.pdf"),
                ),
            ]
            return request.make_response(pdf_content, headers=pdfhttpheaders)
        return request.not_found()

    def _get_document_domain(
        self, model_name, partner, search="", search_in="all"
    ):
        """Build search domain for portal documents based on model type."""
        if model_name == "sale.order":
            domain = [
                ("partner_id", "=", partner.id),
                ("state", "in", ("sale", "done")),
            ]
        elif model_name == "account.move":
            domain = [
                ("partner_id", "=", partner.id),
                ("move_type", "in", ("out_invoice", "out_refund")),
            ]
        elif model_name == "stock.picking":
            domain = [
                ("partner_id", "=", partner.id),
                ("state", "=", "done"),
            ]
        elif model_name == "helpdesk.ticket":
            domain = [("partner_id", "=", partner.id)]
        else:
            domain = [("partner_id", "=", partner.id)]

        if search:
            domain.append(("name", "ilike", search))

        return domain
