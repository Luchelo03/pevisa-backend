from flask import Blueprint, request, jsonify
from db import get_conn

proveedores_bp = Blueprint("proveedores", __name__)

@proveedores_bp.get("/api/proveedores")
def listar_proveedores():
    """
    Devuelve todos los proveedores.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ruc, razon_social, area_especializada, observaciones, telefono, email
                FROM proveedor
                ORDER BY razon_social;
            """)
            rows = cur.fetchall()
    return jsonify(rows), 200


@proveedores_bp.get("/api/proveedores/<ruc>")
def obtener_proveedor(ruc: str):
    """
    Devuelve un proveedor por RUC.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ruc, razon_social, area_especializada, observaciones, telefono, email
                FROM proveedor
                WHERE ruc = %s;
            """, (ruc,))
            row = cur.fetchone()

    if not row:
        return jsonify({"message": "Proveedor no encontrado"}), 404

    return jsonify(row), 200


@proveedores_bp.post("/api/proveedores")
def crear_proveedor():
    """
    Crea un proveedor.
    Espera JSON:
    {
      "ruc": "20123456789",
      "razon_social": "Proveedor X SAC",
      "area_especializada": "...",
      "observaciones": "...",
      "telefono": "...",
      "email": "..."
    }
    """
    data = request.get_json(silent=True) or {}

    ruc = (data.get("ruc") or "").strip()
    razon_social = (data.get("razon_social") or "").strip()

    if not ruc or len(ruc) != 11 or not ruc.isdigit():
        return jsonify({"message": "RUC inválido (debe tener 11 dígitos)"}), 400
    if not razon_social:
        return jsonify({"message": "razon_social es obligatorio"}), 400

    area = data.get("area_especializada")
    obs = data.get("observaciones")
    tel = data.get("telefono")
    email = data.get("email")

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO proveedor (ruc, razon_social, area_especializada, observaciones, telefono, email)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (ruc, razon_social, area, obs, tel, email))
            conn.commit()
        return jsonify({"message": "Proveedor creado", "ruc": ruc}), 201

    except Exception as e:
        # Caso típico: RUC duplicado (unique violation)
        return jsonify({"message": "No se pudo crear proveedor", "error": str(e)}), 400


@proveedores_bp.put("/api/proveedores/<ruc>")
def actualizar_proveedor(ruc: str):
    """
    Actualiza un proveedor por RUC.
    Permite actualizar campos.
    """
    data = request.get_json(silent=True) or {}

    fields = {
        "razon_social": data.get("razon_social"),
        "area_especializada": data.get("area_especializada"),
        "observaciones": data.get("observaciones"),
        "telefono": data.get("telefono"),
        "email": data.get("email"),
    }

    # Nos quedamos solo con los campos enviados (no None)
    updates = {k: v for k, v in fields.items() if v is not None}

    if not updates:
        return jsonify({"message": "No enviaste campos para actualizar"}), 400

    # Armamos SQL dinámico seguro (valores parametrizados)
    set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
    params = list(updates.values()) + [ruc]

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                UPDATE proveedor
                SET {set_clause}
                WHERE ruc = %s;
            """, params)

            if cur.rowcount == 0:
                return jsonify({"message": "Proveedor no encontrado"}), 404

        conn.commit()

    return jsonify({"message": "Proveedor actualizado", "ruc": ruc}), 200


@proveedores_bp.delete("/api/proveedores/<ruc>")
def eliminar_proveedor(ruc: str):
    """
    Elimina proveedor por RUC.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM proveedor WHERE ruc = %s;", (ruc,))
            if cur.rowcount == 0:
                return jsonify({"message": "Proveedor no encontrado"}), 404
        conn.commit()

    return jsonify({"message": "Proveedor eliminado", "ruc": ruc}), 200
