# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django-based financial management system (WEB0020-FINANZAS1) for personal and business finances. The system supports dual database backends (MariaDB/SQLite) and provides comprehensive financial tracking capabilities.

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
# Run tests (if available)
python manage.py test
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

### UI Framework
- **Frontend**: Tailwind CSS with day/night mode toggle
- **Forms**: Django Crispy Forms with Bootstrap5 styling
- **Templates**: Modular template inheritance with `base.html`
- **Responsive design**: Mobile-first approach

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

## Development Notes

### Custom Management Commands
- `db_switch`: Changes active database by updating `.env` file
- `db_copy`: Migrates data between MariaDB and SQLite using Django serializers

### Template System
- Uses Tailwind CSS for styling instead of Bootstrap
- Implements responsive design with container max-widths
- Supports Spanish localization with Mexico City timezone

### PDF Generation
- Uses ReportLab for professional statement generation
- Accessible via `/periodos/<id>/pdf/` endpoint
- Includes formatted financial data with proper decimal handling

## File Structure Highlights
- `core/models.py`: All business logic models and financial calculations
- `core/views.py`: View classes including PDF generation and AJAX endpoints  
- `core/forms.py`: Django forms with custom field filtering
- `guias/manejo-DB.md`: Comprehensive database management guide
- `core/management/commands/`: Custom Django commands for database operations