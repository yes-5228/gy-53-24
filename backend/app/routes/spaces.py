from flask import Blueprint, request

from ..database import get_connection, rows_to_dicts

spaces_bp = Blueprint("spaces", __name__)


@spaces_bp.get("/", strict_slashes=False)
def list_spaces():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM spaces ORDER BY area, code").fetchall()
        stats = conn.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM spaces
            GROUP BY status
            """
        ).fetchall()
    return {"items": rows_to_dicts(rows), "stats": {row["status"]: row["count"] for row in stats}}


@spaces_bp.patch("/<int:space_id>")
def update_space(space_id):
    data = request.get_json() or {}
    status = data.get("status")
    plate_number = data.get("plate_number")
    allowed = {"free", "occupied", "reserved", "maintenance"}

    if status not in allowed:
        return {"message": "车位状态不合法"}, 400

    with get_connection() as conn:
        conn.execute(
            """
            UPDATE spaces
            SET status = ?, plate_number = ?, updated_at = datetime('now', 'localtime')
            WHERE id = ?
            """,
            (status, plate_number if status == "occupied" else None, space_id),
        )
        row = conn.execute("SELECT * FROM spaces WHERE id = ?", (space_id,)).fetchone()

    if not row:
        return {"message": "车位不存在"}, 404
    return dict(row)
