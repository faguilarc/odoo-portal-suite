# odoo-portal-suite

[![Odoo 17](https://img.shields.io/badge/Odoo-17-blue.svg)](https://www.odoo.com)
[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-green.svg)](https://www.gnu.org/licenses/lgpl-3.0)

A collection of Odoo 17 Community modules for building **custom customer and vendor portals** — no Enterprise license required.

## Why This Project?

Most Odoo portal implementations require Enterprise licenses for advanced features. This suite provides **Community-compatible portal tools** that rival Enterprise functionality, enabling freelancers and SMBs to deliver professional portal experiences at zero license cost.

## Modules

| Module | Description | Status |
|--------|-------------|--------|
| `portal_starter` | Base toolkit: custom home, document listing, themes, per-partner branding, invite wizard | ✅ v1.0 |

## portal_starter — Features

- **Custom Portal Home Page** — Card-based document type grid with per-type colors and icons
- **Document Type System** — Admin-configurable document types (orders, invoices, deliveries, etc.) mapped to any Odoo model
- **Per-Partner Branding** — Individual themes, custom CSS, logo override per contact
- **Document Listing & Detail** — Searchable, sortable, paginated document views with PDF download
- **Portal Invite Wizard** — Bulk email invitations with branded HTML template
- **Access Control** — Per-partner document type restrictions, session timeout, login attempt limits
- **Portal Configuration Panel** — Colors, welcome message, social links, custom CSS/JS from Settings
- **4 Built-in Themes** — Default, Modern, Classic, Dark
- **Responsive Design** — Mobile-first CSS with print support
- **Tests** — HttpCase tests included

## Installation

### Option 1: Clone into Odoo addons directory

```bash
cd /opt/odoo17/custom_addons   # or your addons path
git clone https://github.com/faguilarc/odoo-portal-suite.git
```

Add to your `odoo.conf`:

```ini
addons_path = /opt/odoo17/odoo/addons,/opt/odoo17/custom_addons/odoo-portal-suite
```

Restart Odoo and install `portal_starter` from Apps.

### Option 2: As a git submodule

```bash
cd /opt/odoo17/custom_addons
git submodule add https://github.com/faguilarc/odoo-portal-suite.git
git commit -m "Add odoo-portal-suite submodule"
```

## Configuration

After installation, go to **Settings > Administration > Portal Starter**:

1. **Portal Settings** — Customize branding, colors, welcome message
2. **Document Types** — Define which models are visible in the portal
3. **Partner Records** — Enable portal access per contact, set theme and allowed document types
4. **Send Invitations** — Use the invite wizard to send branded email invitations

## Project Structure (OCA Convention)

```
odoo-portal-suite/
├── portal_starter/                    # Addon: Portal Starter Kit
│   ├── __manifest__.py
│   ├── models/                        # Python models
│   ├── views/                         # XML views (backend + frontend)
│   ├── controllers/                   # HTTP controllers
│   ├── wizard/                        # Transient model wizards
│   ├── security/                      # Access rights & groups
│   ├── data/                          # Demo data, email templates
│   ├── static/src/{css,js}/           # Frontend assets
│   └── tests/                         # Test cases
├── .gitignore
├── README.md
└── CONTRIBUTING.md
```

## Branch Policy

| Branch | Odoo Version | Purpose |
|--------|-------------|---------|
| `17.0` | Odoo 17 | Stable development |
| `18.0` | Odoo 18 | Future migration |
| `main` | — | Documentation and meta files |

## Tech Stack

- Python 3.10+
- Odoo 17 Community
- QWeb templates
- OWL (Odoo Web Library) for frontend JS
- SCSS-compatible CSS

## Author

**Fernando Aguilar** — [faguilarc](https://github.com/faguilarc)

Python Full-Stack Developer & Odoo Specialist

## License

[LGPL-3](https://www.gnu.org/licenses/lgpl-3.0) — Same as Odoo Community.