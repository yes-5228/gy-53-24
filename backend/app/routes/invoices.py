from flask import Blueprint, request

from ..database import get_connection, rows_to_dicts
from ..services.invoice import generate_invoice_no

invoices_bp = Blueprint("invoices", __name__)


@invoices_bp.get("/", strict_slashes=False)
def list_invoices():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM invoices ORDER BY id DESC").fetchall()
    return {"items": rows_to_dicts(rows)}


@invoices_bp.post("/", strict_slashes=False)
def create_invoice():
    data = request.get_json() or {}
    required = ["order_id", "buyer_name", "email"]
    if any(not data.get(field) for field in required):
        return {"message": "开票信息不完整"}, 400

    with get_connection() as conn:
        order = conn.execute("SELECT * FROM parking_orders WHERE id = ?", (data["order_id"],)).fetchone()
        if not order:
            return {"message": "停车订单不存在"}, 404
        if order["status"] != "paid":
            return {"message": "仅已结算订单可开具发票"}, 409

        existing = conn.execute("SELECT * FROM invoices WHERE order_id = ?", (data["order_id"],)).fetchone()
        if existing:
            return dict(existing)

        invoice_no = generate_invoice_no(int(data["order_id"]))
        cur = conn.execute(
            """
            INSERT INTO invoices
                (order_id, buyer_name, tax_number, email, amount, issued_at, invoice_no, status)
            VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'), ?, 'issued')
            """,
            (
                data["order_id"],
                data["buyer_name"],
                data.get("tax_number"),
                data["email"],
                order["amount"] or 0,
                invoice_no,
            ),
        )
        row = conn.execute("SELECT * FROM invoices WHERE id = ?", (cur.lastrowid,)).fetchone()

    return dict(row), 201
