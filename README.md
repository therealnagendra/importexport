# Import-Export Documentation & Management System

This project is a local Flask application for managing import-export shipments, parties, agents, documents, tracking milestones, expenses, and reporting.

## Quick start on Windows
1. Install Python 3.11+
2. Open a terminal in this project folder
3. Run `setup.bat`
4. Run `start.bat`
5. Open `http://127.0.0.1:5000`

## First admin setup
Run:

```bat
python app.py create-admin
```
## Demo data
To add fictional sample parties, agents, shipments, tracking milestones, and expenses, run:

```bat
python app.py seed-demo
```

The command can be run again safely; it adds missing demo records without deleting existing data. Demo records use reserved `.example` email addresses and are labeled with `DEMO` shipment references. Normal startup does not insert demo data.

## Testing
```bat
run_tests.bat
```
