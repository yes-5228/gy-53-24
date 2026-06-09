from datetime import datetime


def generate_invoice_no(order_id):
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"INV{stamp}{order_id:04d}"
