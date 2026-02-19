from flask import Blueprint, jsonify
from db import get_conn

despachos_bp = Blueprint("despachos", __name__)

@despachos_bp.get("/api/despachos")
def listar_despachos():
    """
    Devuelve lista para la tabla de Rutas:
    Orden, Descripción, Origen, Destino, Estado, Fecha, y coordenadas.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    d.despacho_id,
                    d.estado,
                    d.fecha_programada,
                    COALESCE(d.descripcion_resumen, '') AS descripcion_resumen,

                    uo.alias AS origen_alias,
                    uo.distrito AS origen_distrito,
                    uo.direccion_texto AS origen_direccion,
                    uo.latitud AS origen_latitud,
                    uo.longitud AS origen_longitud,

                    ud.alias AS destino_alias,
                    ud.distrito AS destino_distrito,
                    ud.direccion_texto AS destino_direccion,
                    ud.latitud AS destino_latitud,
                    ud.longitud AS destino_longitud
                FROM despacho d
                JOIN ubicacion uo ON uo.ubicacion_id = d.ubicacion_origen_id
                JOIN ubicacion ud ON ud.ubicacion_id = d.ubicacion_destino_id
                ORDER BY d.despacho_id DESC;
            """)
            rows = cur.fetchall()

    return jsonify(rows), 200


@despachos_bp.get("/api/despachos/<int:despacho_id>")
def obtener_despacho(despacho_id: int):
    """
    Devuelve un despacho para el modal:
    - cabecera (origen/destino con coords)
    - detalle (productos y cantidades)
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            # 1) Cabecera con origen/destino
            cur.execute("""
                SELECT
                    d.despacho_id,
                    d.estado,
                    d.fecha_programada,
                    d.venta_id,
                    COALESCE(d.descripcion_resumen, '') AS descripcion_resumen,

                    uo.alias AS origen_alias,
                    uo.distrito AS origen_distrito,
                    uo.direccion_texto AS origen_direccion,
                    uo.latitud AS origen_latitud,
                    uo.longitud AS origen_longitud,

                    ud.alias AS destino_alias,
                    ud.distrito AS destino_distrito,
                    ud.direccion_texto AS destino_direccion,
                    ud.latitud AS destino_latitud,
                    ud.longitud AS destino_longitud
                FROM despacho d
                JOIN ubicacion uo ON uo.ubicacion_id = d.ubicacion_origen_id
                JOIN ubicacion ud ON ud.ubicacion_id = d.ubicacion_destino_id
                WHERE d.despacho_id = %s;
            """, (despacho_id,))
            head = cur.fetchone()

            if not head:
                return jsonify({"message": "Despacho no encontrado"}), 404

            # 2) Detalle: productos enviados
            cur.execute("""
                SELECT
                    dd.despacho_detalle_id,
                    p.producto_id,
                    p.numero_serial,
                    p.nombre,
                    dd.cantidad
                FROM despacho_detalle dd
                JOIN producto p ON p.producto_id = dd.producto_id
                WHERE dd.despacho_id = %s
                ORDER BY p.nombre;
            """, (despacho_id,))
            detalle = cur.fetchall()

    return jsonify({
        "cabecera": head,
        "detalle": detalle
    }), 200
