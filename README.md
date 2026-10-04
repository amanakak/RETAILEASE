# RetailEase

RetailEase is a Django inventory, sales, and point-of-sale system for small and medium-sized shops.

## Features

- Product, category, SKU, barcode, and stock management
- POS sales with product search, receipts, and change calculation
- Customer records, purchase history, and loyalty points
- Admin dashboards, reports, analytics, and low-stock alerts
- Expense and supplier management
- Separate administrator and staff access

## Loyalty programme

- Earn 1 point for every ₹100 spent.
- 1 point gives ₹1.20 discount on a future purchase.
- Cash customers can round a bill up to the next rupee and convert the difference into points.
- Guest customers do not earn or redeem points.

## Requirements

- Python 3.8 or newer
- pip

## Setup on Windows

Open a terminal in the folder containing `manage.py`:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py create_sample_data
python manage.py runserver 127.0.0.1:8001
```

Open [http://127.0.0.1:8001](http://127.0.0.1:8001).

On macOS or Linux, activate the environment with `source venv/bin/activate`.

## Demo accounts

| Role | Username | Password |
| --- | --- | --- |
| Administrator | `admin` | `admin123` |
| Staff | `staff` | `staff123` |

Change these passwords before using the application outside local development.

## Currency

RetailEase uses Indian rupees (`₹`) throughout the application. Existing demonstration dollar values are converted during migration using `$1 = ₹90`. New prices should be entered directly in rupees.

## Useful commands

```powershell
python manage.py check
python manage.py migrate
python manage.py runserver 127.0.0.1:8001
```

Stop the server with `Ctrl+C`.

## Troubleshooting

If port 8001 is unavailable, use `python manage.py runserver 127.0.0.1:8080`.

For a CSRF error, close old browser tabs, restart the server, use one address consistently, and log in again.

If the database is read-only, make sure the project folder and `db.sqlite3` are writable, then run `attrib -R db.sqlite3` followed by `python manage.py migrate`.

## Production notes

Before deployment, set `DEBUG = False`, use a secure secret key, configure allowed hosts, use PostgreSQL or MySQL, serve static files properly, and enable HTTPS.

## License

Educational and demonstration project.
