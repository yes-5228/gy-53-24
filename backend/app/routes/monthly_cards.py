from flask import Blueprint, request

from ..database import get_connection, rows_to_dicts

monthly_cards_bp = Blueprint("monthly_cards", __name__)


@monthly_cards_bp.get("/", strict_slashes=False)
def list_cards():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM monthly_cards ORDER BY id DESC").fetchall()
    return {"items": rows_to_dicts(rows)}


@monthly_cards_bp.post("/", strict_slashes=False)
def create_card():
    data = request.get_json() or {}
    required = ["holder_name", "phone", "plate_number", "start_date", "end_date", "fee"]
    if any(not data.get(field) for field in required):
        return {"message": "月卡信息不完整"}, 400

    try:
        with get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO monthly_cards
                    (holder_name, phone, plate_number, start_date, end_date, fee, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["holder_name"],
                    data["phone"],
                    data["plate_number"],
                    data["start_date"],
                    data["end_date"],
                    float(data["fee"]),
                    data.get("status", "active"),
                ),
            )
            row = conn.execute("SELECT * FROM monthly_cards WHERE id = ?", (cur.lastrowid,)).fetchone()
    except Exception as exc:
        if "UNIQUE" in str(exc):
            return {"message": "该车牌已办理月卡"}, 409
        raise

    return dict(row), 201


@monthly_cards_bp.patch("/<int:card_id>")
def update_card(card_id):
    data = request.get_json() or {}
    status = data.get("status")
    if status not in {"active", "expired", "paused"}:
        return {"message": "月卡状态不合法"}, 400

    with get_connection() as conn:
        conn.execute("UPDATE monthly_cards SET status = ? WHERE id = ?", (status, card_id))
        row = conn.execute("SELECT * FROM monthly_cards WHERE id = ?", (card_id,)).fetchone()

    if not row:
        return {"message": "月卡不存在"}, 404
    return dict(row)
