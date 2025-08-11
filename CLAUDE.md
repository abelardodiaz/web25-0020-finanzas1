# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django-based financial management system (WEB0020-FINANZAS1) for personal and business finances. The system supports dual database backends (MariaDB/SQLite) and provides comprehensive financial tracking capabilities.

**Current Version**: v0.6.0 (August 2025) - Revolucion de Simplicidad
**Python**: 3.12+ with modern type hints
**UI Framework**: Tailwind CSS with dark/light mode support

## Development Commands

### Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Database Management
The project supports both MariaDB and SQLite databases with custom management commands:

```bash
# Switch between databases
python manage.py db_switch sqlite
python manage.py db_switch mariadb

# Copy data between databases
python manage.py db_copy --from mariadb --to sqlite
python manage.py db_copy --from sqlite --to mariadb --keep

# Standard Django database operations
python manage.py makemigrations
python manage.py migrate
python manage.py migrate --database=sqlite
python manage.py migrate --database=mariadb

# Check migrations status
python manage.py showmigrations --database=sqlite
```

### Development Server
```bash
# Run development server
python manage.py runserver

# Database checks
python manage.py check --database default

# Create superuser
python manage.py createsuperuser
```

### Testing
```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test core

# Run specific test class
python manage.py test core.tests.TestClassName

# Run with verbose output
python manage.py test --verbosity=2
```

## Architecture Overview

### Core Application Structure
- **Main Django project**: `config/` - Contains settings, URLs, WSGI configuration
- **Core app**: `core/` - Primary business logic, models, views, forms
- **Templates**: `templates/` - HTML templates organized by functionality
- **Static files**: `static/` - CSS and static assets

### Database Configuration
The project uses a dual-database architecture:
- **MariaDB**: Production database with full MySQL compatibility
- **SQLite**: Development/backup database
- **Database switching**: Controlled via `ACTIVE_DB` environment variable
- **Custom commands**: `db_switch` and `db_copy` for database management

### Key Models and Business Logic
The system models financial concepts through:
- **TipoCuenta**: Account types (Debit, Credit, Services, Income) with account nature (Deudora/Acreedora)
- **Cuenta**: Bank accounts with automatic balance calculations
- **Categoria**: Hierarchical transaction categories (Personal/Business)
- **Transaccion**: Financial transactions with automatic sign handling
- **Periodo**: Billing periods for credit cards and services
- **Recurrencia**: Recurring payment schedules

### Financial Flow Architecture
The system implements account nature-based transaction flow:
- **Deudora accounts**: Increases with debits, decreases with credits
- **Acreedora accounts**: Increases with credits, decreases with debits
- **Automatic sign handling**: Expenses are negative, income positive
- **Transfer handling**: Dual-entry system for inter-account transfers
- **Transaction Grouping**: Uses `grupo_uuid` to link related transactions (transfers, service payments)
- **Account Types**: DEB (Debit), CRE (Credit), SER (Services), ING (Income) with different business rules

### UI Framework (v0.5.5)
- **Frontend**: Tailwind CSS with consistent dark/light mode implementation
- **Forms**: Django Widget Tweaks for custom styling (Bootstrap5 removed)
- **Templates**: Modular template inheritance with enhanced `base.html`
- **Design System**: Standardized components in `STYLE_GUIDE.md`
- **Typography**: `text-lg` standard for forms, consistent spacing (`py-2 px-3`)
- **Theme Toggle**: Persistent localStorage-based dark/light mode switching

### Features Overview
- **Account Management**: Multi-currency support (MXN/USD), account grouping
- **Transaction Processing**: Categorized transactions, reconciliation, transfers
- **Billing Periods**: Credit card and service billing with PDF generation
- **PDF Reports**: Professional account statements using ReportLab
- **AJAX Updates**: Dynamic form field refreshing
- **User Authentication**: Built-in Django auth with profile management

## Environment Configuration

The project uses `django-environ` for configuration management:
- **Required variables**: `SECRET_KEY`, `DATABASE_URL`
- **Optional variables**: `DEBUG`, `ACTIVE_DB` (mariadb|sqlite)
- **Database URL format**: `mysql://user:password@host:port/database`

### Critical Dependencies
```
Django>=5.2
django-environ
mariadb
mysqlclient
django-filter
django-widget-tweaks
pandas
openpyxl
reportlab
```

## Development Notes

### Custom Management Commands
- `db_switch`: Changes active database by updating `.env` file
- `db_copy`: Migrates data between MariaDB and SQLite using Django serializers

### AJAX Endpoints
- `/cuentas-servicio-json/`: Service accounts for dropdowns
- `/categorias-json/`: Categories for dropdowns  
- `/medios-pago-json/`: Payment methods for dropdowns
- `/cuentas-autocomplete/`: Account autocomplete by group
- `/cuenta-movimientos/`: Paginated account movements

### Template System
- **Complete Tailwind Migration**: All Bootstrap dependencies removed
- **Consistent Styling**: Standard classes defined in `STYLE_GUIDE.md`
- **Form Standards**: `text-lg py-2 px-3 w-full rounded border border-gray-300 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500`
- **Date Inputs**: Centralized styling in `static/css/styles.css` with native `color-scheme` support
- **Responsive Design**: Mobile-first with container max-widths
- **Localization**: Spanish with Mexico City timezone

### PDF Generation
- Uses ReportLab for professional statement generation
- Accessible via `/periodos/<id>/pdf/` endpoint
- Includes formatted financial data with proper decimal handling

## Code Quality Standards

### Python 3.12 Type Hints
All core modules use modern Python 3.12 type hints:
```python
from __future__ import annotations
from typing import Any
from django.http import HttpRequest, HttpResponse, JsonResponse

def view_method(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    return super().view_method(request, *args, **kwargs)

def clean(self) -> dict[str, Any]:
    return super().clean()

def save(self, commit: bool = True) -> ModelClass:
    return super().save(commit=commit)
```

### Form Validation Patterns
```python
def clean(self) -> dict[str, Any]:
    cleaned_data = super().clean()
    # Custom validation logic
    return cleaned_data

def save(self, commit: bool = True) -> ModelClass:
    obj = super().save(commit=False)
    # Custom save logic
    if commit:
        obj.save()
    return obj
```

## File Structure Highlights
- `core/models.py`: Business logic models with financial calculations and managers
- `core/views.py`: Modern view classes with full type hints, PDF generation, AJAX endpoints
- `core/forms.py`: Django forms with Python 3.12 type hints and custom field filtering
- `templates/base.html`: Enhanced navigation with dropdown menus and theme toggle
- `static/css/styles.css`: Centralized styles for native elements (date inputs)
- `STYLE_GUIDE.md`: Complete UI component reference with dark/light mode examples
- `changelog_claude.md`: Detailed development history with technical metrics
- `guias/manejo-DB.md`: Comprehensive database management guide
- `core/management/commands/`: Custom Django commands for database operations
```

## Environment Best Practices

- **Python Version**: 
  - Usa python3 en todos los casos y activa el entorno virtual para poder ejecutar comandos python o el shell de django, etc

## Development Server Notes
- usa en puerto random entre 8200 y 8300 para ejecutar django server 

## Project File Memories

### Key File Reference
- `@guias/registros_contables.md` - Critical file for understanding account logic and nature of creditor and debtor accounts in the financial system
  - Version 2 contains detailed information about result accounts, asset accounts, and liability accounts
  - Accounts are differentiated in the system by `es_medio_pago = true` or `es_medio_pago = false`

### Language Reference
- **sig** significa "siguiente"

### Weird Moments
- o que la chingada son 12 + 50 + 50, no te equivoques con eso