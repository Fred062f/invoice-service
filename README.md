# Invoice Service API

This is a RESTful API built using Flask for managing invoices. It allows users to create, retrieve, update, and delete invoices, while ensuring security using JWT authentication. The service supports filtering and sorting invoices, and provides detailed API documentation via Swagger.

## Features

- **Create an Invoice**: Add a new invoice by providing the required details.
- **Get Invoices**: Retrieve all invoices or filter by subscription ID, payment status, and sort by different fields.
- **Update an Invoice**: Modify the details of an existing invoice.
- **Delete an Invoice**: Remove an invoice from the system by its ID.
- **Swagger UI**: Automatically generated interactive API documentation.
- **JWT Authentication**: Secure access to endpoints using JWT tokens.

## Installation

### Prerequisites

- Python 3.x
- pip (Python package installer)
- SQLite

### Steps to Run

1. Clone this repository or download the code.

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your `.env` file with the following environment variables:

   ```
   DATABASE=path_to_your_database.db
   SECRET_KEY=your_jwt_secret_key
   ```

4. Initialize the database by running the following command (if your `init_db()` function does not already set up the necessary tables):

   ```bash
   python -c "from db import init_db; init_db()"
   ```

5. Run the Flask app:

   ```bash
   python app.py
   ```

6. The API will be available at `http://localhost:5000`.

## API Endpoints

### Authentication

All endpoints require a valid JWT token to be passed in the `Authorization` header. The token must be prefixed with `Bearer `.

### Endpoints:

#### `POST /invoices`
- **Create a new invoice**.
- Requires authentication (`JWT`).
- **Parameters**: 
  - `subscription_id`: ID of the subscription.
  - `amount`: Amount of the invoice.
  - `invoice_date`: Date when the invoice is created.
  - `due_date`: Date when payment is due.
  - `payment_status`: Payment status (`Paid`, `Pending`, `Overdue`).
  - `description`: Invoice description.

#### `GET /invoices`
- **Get all invoices** or filter invoices by parameters.
- Requires authentication (`JWT`).
- **Parameters**:
  - `subscription_id`: Filter by subscription ID.
  - `payment_status`: Filter by payment status.
  - `sort_by`: Field to sort by (`due_date`, `total_amount`, `invoice_date`).
  - `sort_order`: Sort order (`asc` or `desc`).

#### `PUT /invoices/<int:invoice_id>`
- **Update an existing invoice** by its ID.
- Requires authentication (`JWT`).
- **Parameters**: 
  - `invoice_id`: The ID of the invoice to update.
  - Fields to update: `amount`, `invoice_date`, `due_date`, `payment_status`, `description`.

#### `DELETE /invoices/<int:invoice_id>`
- **Delete an invoice** by its ID.
- Requires authentication (`JWT`).
- **Parameters**:
  - `invoice_id`: The ID of the invoice to delete.

#### `GET /endpoints`
- **List all available endpoints** in the API.
- No authentication required.

## API Documentation

Swagger UI is available at `/apidocs/` for detailed API documentation. It provides an interactive interface to test API endpoints.

## Database

The API uses SQLite as the database to store invoice data. The database file location is specified in the `.env` file under `DATABASE`.
