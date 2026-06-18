# Contributing to odoo-portal-suite

Thank you for your interest in contributing! This project follows [OCA conventions](https://github.com/OCA/odoo-community.org).

## Branch Naming

- `17.0` — Odoo 17 development branch (main development happens here)
- `17.0-<feature-name>` — Feature branches
- `main` — Documentation and project-level files only

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```
feat(portal_starter): add dark theme support
fix(portal_starter): fix pagination on document list
docs: update README installation instructions
```

## Adding a New Addon

1. Create a new directory at the repo root: `your_addon_name/`
2. Include at minimum: `__init__.py`, `__manifest__.py`, `models/`, `views/`
3. Follow OCA naming conventions (snake_case, no dots in addon names)
4. Add your addon to this README's module table
5. Open a Pull Request against the `17.0` branch

## Code Style

- **Python**: PEP 8, use `flake8` and `pylint-odoo`
- **XML**: 4-space indentation, meaningful `id` attributes
- **JavaScript**: OWL framework patterns, ES6+
- **CSS**: BEM-like naming, mobile-first

## Running Tests

```bash
cd /opt/odoo17
./odoo-bin -c odoo.conf -d test_db \
    --test-enable \
    --test-tags /portal_starter \
    --stop-after-init
```

## Reporting Issues

Please use [GitHub Issues](https://github.com/faguilarc/odoo-portal-suite/issues) with:
- Odoo version
- Module version
- Steps to reproduce
- Expected vs actual behavior
- Relevant log excerpts

## License

All contributions fall under the LGPL-3 license, consistent with Odoo Community.