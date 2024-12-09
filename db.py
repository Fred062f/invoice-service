import sqlite3
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import random

load_dotenv()
DATABASE = os.getenv("DATABASE")

def init_db():
    """
    Initializes the Invoices database and populates it with sample data.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subscription_id INTEGER NOT NULL,
        amount DECIMAL(10, 2) NOT NULL,
        invoice_date DATE NOT NULL,
        due_date DATE NOT NULL,
        payment_status TEXT CHECK(payment_status IN ('Paid', 'Pending', 'Overdue')) NOT NULL,
        description TEXT NOT NULL
    )
    """)

    # Sample data for subscriptions
    subscriptions_data = [
        # (subscription_id, price_per_month, down_payment)
        (1, 1200.00, 500.00),
        (2, 1000.00, 400.00),
        (3, 1100.00, 450.00),
    ]

    payment_statuses = ['Paid', 'Pending', 'Overdue']
    today = datetime.today()

    for subscription in subscriptions_data:
        subscription_id, price_per_month, down_payment = subscription

        # Generate down payment invoice (one-time)
        down_payment_invoice = (
            subscription_id,
            down_payment,
            today.strftime("%Y-%m-%d"),  # Invoice date
            (today + timedelta(days=7)).strftime("%Y-%m-%d"),  # Due date
            random.choice(payment_statuses),  # Payment status
            "Down payment for subscription"
        )
        cursor.execute("""
        INSERT INTO invoices (subscription_id, amount, invoice_date, due_date, payment_status, description)
        VALUES (?, ?, ?, ?, ?, ?)
        """, down_payment_invoice)

        # Generate recurring monthly payment invoices
        for i in range(1, 4):  # Generate 3 months of invoices
            invoice_date = today + timedelta(days=30 * i)
            due_date = invoice_date + timedelta(days=7)
            monthly_invoice = (
                subscription_id,
                price_per_month,
                invoice_date.strftime("%Y-%m-%d"),
                due_date.strftime("%Y-%m-%d"),
                random.choice(payment_statuses),
                "Monthly subscription payment"
            )
            cursor.execute("""
            INSERT INTO invoices (subscription_id, amount, invoice_date, due_date, payment_status, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """, monthly_invoice)

    conn.commit()
    conn.close()
    print("Invoices table initialized and populated with sample data.")

if __name__ == "__main__":
    init_db()
