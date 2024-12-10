from flask import Flask, request, jsonify
import sqlite3
from flasgger import Swagger
import os
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, jwt_required
from db import init_db
import inspect

load_dotenv()

app = Flask(__name__)

DATABASE = os.getenv("DATABASE")
SECRET_KEY = os.getenv('SECRET_KEY')

app.config['JWT_SECRET_KEY'] = SECRET_KEY
jwt = JWTManager(app)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter your JWT token in the format **Bearer &lt;token&gt;**.",
        }
    },
    "security": [{"BearerAuth": []}],
}
swagger = Swagger(app, config=swagger_config)

init_db()

@app.route('/invoices', methods=['POST'])
@jwt_required()
def create_invoice():
    """
    Create a new invoice.
    ---
    tags:
      - Invoices
    security:
      - BearerAuth: []
    parameters:
      - name: body
        in: body
        required: true
        description: Invoice details
        schema:
          type: object
          properties:
            subscription_id:
              type: integer
              description: ID of the subscription
            amount:
              type: number
              description: Amount of the invoice
            invoice_date:
              type: string
              format: date
              description: Invoice creation date
            due_date:
              type: string
              format: date
              description: Due date for the invoice
            payment_status:
              type: string
              enum: [Paid, Pending, Overdue]
              description: Payment status of the invoice
            description:
              type: string
              description: Invoice description
    responses:
      201:
        description: Invoice successfully created.
      400:
        description: Missing required fields.
      401:
        description: Unauthorized.
    """
    data = request.get_json()
    required_fields = ["subscription_id", "amount", "invoice_date", "due_date", "payment_status", "description"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.execute("""
        INSERT INTO invoices (subscription_id, amount, invoice_date, due_date, payment_status, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["subscription_id"], data["amount"], data["invoice_date"], 
        data["due_date"], data["payment_status"], data["description"]
    ))
    conn.commit()
    invoice_id = cursor.lastrowid
    conn.close()

    return jsonify({"id": invoice_id, "message": "Invoice created successfully"}), 201


@app.route('/invoices', methods=['GET'])
@jwt_required()
def get_invoices():
    """
    Retrieve all invoices or filter by parameters with sorting capabilities.
    ---
    tags:
      - Invoices
    security:
      - BearerAuth: []
    parameters:
      - name: subscription_id
        in: query
        type: integer
        description: Filter invoices by subscription ID.
      - name: payment_status
        in: query
        type: string
        description: Filter invoices by payment status.
      - name: sort_by
        in: query
        type: string
        description: Field to sort by (e.g., due_date, total_amount).
      - name: sort_order
        in: query
        type: string
        description: Sort order (asc or desc). Default is asc.
    responses:
      200:
        description: List of invoices.
      401:
        description: Unauthorized.
    """
    filters = []
    query = "SELECT * FROM invoices WHERE 1=1"

    # Filtering
    subscription_id = request.args.get("subscription_id")
    if subscription_id:
        query += " AND subscription_id = ?"
        filters.append(subscription_id)

    payment_status = request.args.get("payment_status")
    if payment_status:
        query += " AND payment_status = ?"
        filters.append(payment_status)

    # Sorting
    sort_by = request.args.get("sort_by")
    sort_order = request.args.get("sort_order", "asc").lower()
    valid_sort_orders = ["asc", "desc"]
    valid_sort_fields = ["due_date", "total_amount", "invoice_date"]

    if sort_by in valid_sort_fields:
        if sort_order not in valid_sort_orders:
            return jsonify({"error": "Invalid sort order. Use 'asc' or 'desc'."}), 400
        query += f" ORDER BY {sort_by} {sort_order}"

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(query, filters)
    rows = cursor.fetchall()
    conn.close()

    invoices = [dict(row) for row in rows]
    return jsonify(invoices), 200


@app.route('/invoices/<int:invoice_id>', methods=['PUT'])
@jwt_required()
def update_invoice(invoice_id):
    """
    Update an invoice by ID.
    ---
    tags:
      - Invoices
    security:
      - BearerAuth: []
    parameters:
      - name: invoice_id
        in: path
        type: integer
        required: true
        description: ID of the invoice to update.
      - name: body
        in: body
        required: true
        description: Updated invoice details.
    responses:
      200:
        description: Invoice successfully updated.
      404:
        description: Invoice not found.
    """
    data = request.get_json()
    updates = []
    params = []

    for key in ["amount", "invoice_date", "due_date", "payment_status", "description"]:
        if key in data:
            updates.append(f"{key} = ?")
            params.append(data[key])

    if not updates:
        return jsonify({"error": "No fields to update"}), 400

    query = f"UPDATE invoices SET {', '.join(updates)} WHERE invoice_id = ?"
    params.append(invoice_id)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.execute(query, params)
    conn.commit()
    row_count = cursor.rowcount
    conn.close()

    if row_count == 0:
        return jsonify({"error": "Invoice not found"}), 404

    return jsonify({"message": "Invoice updated successfully"}), 200


@app.route('/invoices/<int:invoice_id>', methods=['DELETE'])
@jwt_required()
def delete_invoice(invoice_id):
    """
    Delete an invoice by ID.
    ---
    tags:
      - Invoices
    security:
      - BearerAuth: []
    parameters:
      - name: invoice_id
        in: path
        type: integer
        required: true
        description: ID of the invoice to delete.
    responses:
      200:
        description: Invoice successfully deleted.
      404:
        description: Invoice not found.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.execute("DELETE FROM invoices WHERE invoice_id = ?", (invoice_id,))
    conn.commit()
    row_count = cursor.rowcount
    conn.close()

    if row_count == 0:
        return jsonify({"error": "Invoice not found"}), 404

    return jsonify({"message": "Invoice deleted successfully"}), 200


@app.route('/endpoints', methods=['GET'])
def endpoints():
    """
    List all available endpoints in the API, including their descriptions, methods, and JWT token requirements.
    --- 
    tags:
      - Utility
    responses:
      200:
        description: A list of all available routes with their descriptions, methods, and JWT token requirements.
    """
    excluded_endpoints = {'static', 'flasgger.static', 'flasgger.oauth_redirect', 'flasgger.<lambda>', 'flasgger.apispec'}
    excluded_methods = {'HEAD', 'OPTIONS'}
    routes = []

    for rule in app.url_map.iter_rules():
        if rule.endpoint not in excluded_endpoints:
            func = app.view_functions.get(rule.endpoint)
            if not func:
                continue

            # Get the docstring
            full_docstring = inspect.getdoc(func)
            docstring = full_docstring.split('---')[0].replace("\n", " ").strip() if full_docstring else None

            # Check if the @jwt_required() decorator is applied
            jwt_required = "@jwt_required" in inspect.getsource(func).split('\n')[1]

            # Exclude methods
            methods = list(rule.methods - excluded_methods)

            routes.append({
                'endpoint': rule.rule,
                'methods': methods,
                'description': docstring,
                'jwt_required': jwt_required
            })
    return jsonify({'endpoints': routes}), 200


if __name__ == "__main__":
    app.run(debug=True)
