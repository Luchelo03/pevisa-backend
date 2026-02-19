from flask import Blueprint, jsonify, request
from db import get_conn

reportes_bp = Blueprint("reportes", __name__)

@reportes_bp.get("/api/reportes/top-vendedores")
def top_vendedores():
    """
    Top vendedores por utilidad.
    Query params opcionales:
      - limit (default 10)
    Usa utilidad_total de la cabecera de venta.
    """
    limit = request.args.get("limit", default=10, type=int)
    if limit <= 0 or limit > 100:
        limit = 10

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    v.dni AS dni_vendedor,
                    v.nombre AS vendedor,
                    COUNT(*) AS ventas_realizadas,
                    COALESCE(SUM(ve.total_venta), 0) AS total_venta,
                    COALESCE(SUM(ve.utilidad_total), 0) AS utilidad_total
                FROM venta ve
                JOIN vendedor v ON v.dni = ve.dni_vendedor
                WHERE ve.estado = 'REGISTRADA'
                GROUP BY v.dni, v.nombre
                ORDER BY utilidad_total DESC
                LIMIT %s;
            """, (limit,))
            rows = cur.fetchall()

    return jsonify(rows), 200


@reportes_bp.get("/api/reportes/top-vendedores-detalle")
def top_vendedores_por_detalle():
    """
    Top vendedores por utilidad calculada desde VentaDetalle.
    Útil si quieres asegurar consistencia incluso si alguien no actualiza cabecera.
    """
    limit = request.args.get("limit", default=10, type=int)
    if limit <= 0 or limit > 100:
        limit = 10

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    v.dni AS dni_vendedor,
                    v.nombre AS vendedor,
                    COUNT(DISTINCT ve.venta_id) AS ventas_realizadas,
                    COALESCE(SUM(vd.subtotal_venta), 0) AS total_venta,
                    COALESCE(SUM(vd.utilidad_linea), 0) AS utilidad_total
                FROM venta ve
                JOIN vendedor v ON v.dni = ve.dni_vendedor
                JOIN venta_detalle vd ON vd.venta_id = ve.venta_id
                WHERE ve.estado = 'REGISTRADA'
                GROUP BY v.dni, v.nombre
                ORDER BY utilidad_total DESC
                LIMIT %s;
            """, (limit,))
            rows = cur.fetchall()

    return jsonify(rows), 200
