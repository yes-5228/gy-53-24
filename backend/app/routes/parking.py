from collections import Counter
from datetime import datetime

from flask import Blueprint, request

from ..database import get_connection, rows_to_dicts
from ..services.billing import calculate_fee

parking_bp = Blueprint("parking", __name__)


@parking_bp.get("/orders")
def list_orders():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM parking_orders ORDER BY id DESC LIMIT 100").fetchall()
    return {"items": rows_to_dicts(rows)}


@parking_bp.post("/entry")
def create_entry():
    data = request.get_json() or {}
    plate_number = data.get("plate_number")
    space_code = data.get("space_code")
    if not plate_number or not space_code:
        return {"message": "车牌号和车位号不能为空"}, 400

    with get_connection() as conn:
        space = conn.execute("SELECT * FROM spaces WHERE code = ?", (space_code,)).fetchone()
        if not space:
            return {"message": "车位不存在"}, 404
        if space["status"] not in {"free", "reserved"}:
            return {"message": "车位当前不可入场"}, 409

        entry_time = data.get("entry_time") or datetime.now().isoformat(timespec="minutes")
        cur = conn.execute(
            """
            INSERT INTO parking_orders (plate_number, space_code, entry_time, status)
            VALUES (?, ?, ?, 'parking')
            """,
            (plate_number, space_code, entry_time),
        )
        conn.execute(
            """
            UPDATE spaces
            SET status = 'occupied', plate_number = ?, updated_at = datetime('now', 'localtime')
            WHERE code = ?
            """,
            (plate_number, space_code),
        )
        row = conn.execute("SELECT * FROM parking_orders WHERE id = ?", (cur.lastrowid,)).fetchone()

    return dict(row), 201


@parking_bp.post("/calculate")
def calculate():
    data = request.get_json() or {}
    if not data.get("entry_time") or not data.get("exit_time"):
        return {"message": "入场时间和离场时间不能为空"}, 400
    return calculate_fee(data["entry_time"], data["exit_time"])


@parking_bp.post("/exit/<int:order_id>")
def close_order(order_id):
    data = request.get_json() or {}
    exit_time = data.get("exit_time") or datetime.now().isoformat(timespec="minutes")

    with get_connection() as conn:
        order = conn.execute("SELECT * FROM parking_orders WHERE id = ?", (order_id,)).fetchone()
        if not order:
            return {"message": "停车订单不存在"}, 404
        if order["status"] == "paid":
            return {"message": "订单已结算"}, 409

        bill = calculate_fee(order["entry_time"], exit_time)
        conn.execute(
            """
            UPDATE parking_orders
            SET exit_time = ?, duration_hours = ?, amount = ?, status = 'paid'
            WHERE id = ?
            """,
            (exit_time, bill["duration_hours"], bill["amount"], order_id),
        )
        conn.execute(
            """
            UPDATE spaces
            SET status = 'free', plate_number = NULL, updated_at = datetime('now', 'localtime')
            WHERE code = ?
            """,
            (order["space_code"],),
        )
        row = conn.execute("SELECT * FROM parking_orders WHERE id = ?", (order_id,)).fetchone()

    return dict(row)


@parking_bp.get("/revenue/daily")
def daily_revenue():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT exit_time, amount
            FROM parking_orders
            WHERE status = 'paid' AND exit_time IS NOT NULL
            ORDER BY exit_time DESC
            """
        ).fetchall()

    daily_stats = {}
    for row in rows:
        exit_time_str = row["exit_time"]
        exit_dt = datetime.fromisoformat(exit_time_str.replace("Z", "+00:00")).replace(tzinfo=None)
        date_key = exit_dt.strftime("%Y-%m-%d")
        hour_key = exit_dt.hour

        if date_key not in daily_stats:
            daily_stats[date_key] = {
                "date": date_key,
                "total_amount": 0.0,
                "free_count": 0,
                "order_count": 0,
                "hour_counter": Counter(),
            }

        daily_stats[date_key]["total_amount"] += row["amount"] or 0.0
        daily_stats[date_key]["order_count"] += 1
        if (row["amount"] or 0) == 0:
            daily_stats[date_key]["free_count"] += 1
        daily_stats[date_key]["hour_counter"][hour_key] += 1

    result = []
    for date_key in sorted(daily_stats.keys(), reverse=True):
        stat = daily_stats[date_key]
        peak_hour = None
        if stat["hour_counter"]:
            peak_hour, _ = stat["hour_counter"].most_common(1)[0]
        result.append({
            "date": stat["date"],
            "total_amount": round(stat["total_amount"], 2),
            "free_count": stat["free_count"],
            "order_count": stat["order_count"],
            "peak_hour": f"{peak_hour:02d}:00-{(peak_hour + 1) % 24:02d}:00" if peak_hour is not None else "-",
        })

    return {"items": result}
