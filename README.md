# (Django + TallyPrime + MySQL Database )

1. Set Up TallyPrime

- Create a Company in TallyPrime using the "Create Company" option.
- Enable TallyPort:
- Go to F12 → Advanced Configuration → Enable ODBC Server.
- Set the TallyPort number (default is 9000, but you can change it )
- Ensure that the TallyPrime port and the Django runserver port are different to avoid conflicts.

2. Database Setup
- This project uses MySQL as the primary database.
- However, you can also configure SQLite or PostgreSQL (pgAdmin) if preferred by updating the DATABASES
configuration in settings.py.

3. Features Implemented
- Stock Groups
- Stock Categories
- Stock Items
- Groups
- Ledgers
- Sales Voucher
- Balanced Sheet
