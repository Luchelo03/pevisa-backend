from flask import Blueprint, request, jsonify
from db import get_conn

clientes_bp = Blueprint("clientes", __name__)

@clientes_bp.get("/api/clientes")
def listar_clientes():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT cliente_id, dni_ruc, nombre_razon_social, telefono, email
                FROM cliente
                ORDER BY nombre_razon_social;
            """)
            rows = cur.fetchall()
    return jsonify(rows), 200


@clientes_bp.get("/api/clientes/<int:cliente_id>")
def obtener_cliente(cliente_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT cliente_id, dni_ruc, nombre_razon_social, telefono, email
                FROM cliente
                WHERE cliente_id = %s;
            """, (cliente_id,))
            row = cur.fetchone()

    if not row:
        return jsonify({"message": "Cliente no encontrado"}), 404

    return jsonify(row), 200


@clientes_bp.post("/api/clientes")
def crear_cliente():
    """
    JSON esperado:
    {
      "dni_ruc": "48221109",
      "nombre_razon_social": "Juan Pérez",
      "telefono": "999111222",
      "email": "juan@gmail.com"
    }
    """
    data = request.get_json(silent=True) or {}

    dni_ruc = (data.get("dni_ruc") or "").strip()
    nombre = (data.get("nombre_razon_social") or "").strip()
    telefono = data.get("telefono")
    email = data.get("email")

    if not dni_ruc:
        return jsonify({"message": "dni_ruc es obligatorio"}), 400
    if not nombre:
        return jsonify({"message": "nombre_razon_social es obligatorio"}), 400

    # Validación ligera: si parece DNI (8) o RUC (11), que sean numéricos
    if len(dni_ruc) in (8, 11) and not dni_ruc.isdigit():
        return jsonify({"message": "dni_ruc inválido (debe ser numérico si es DNI/RUC)"}), 400

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO cliente (dni_ruc, nombre_razon_social, telefono, email)
                    VALUES (%s, %s, %s, %s)
                    RETURNING cliente_id;
                """, (dni_ruc, nombre, telefono, email))
                new_id = cur.fetchone()["cliente_id"]
            conn.commit()

        return jsonify({"message": "Cliente creado", "cliente_id": new_id}), 201

    except Exception as e:
        return jsonify({"message": "No se pudo crear cliente", "error": str(e)}), 400


@clientes_bp.put("/api/clientes/<int:cliente_id>")
def actualizar_cliente(cliente_id: int):
    data = request.get_json(silent=True) or {}

    fields = {
        "dni_ruc": data.get("dni_ruc"),
        "nombre_razon_social": data.get("nombre_razon_social"),
        "telefono": data.get("telefono"),
        "email": data.get("email"),
    }

    updates = {k: v for k, v in fields.items() if v is not None}

    if not updates:
        return jsonify({"message": "No enviaste campos para actualizar"}), 400

    # Validación ligera si envían dni_ruc
    if "dni_ruc" in updates:
        dni_ruc = (updates["dni_ruc"] or "").strip()
        if not dni_ruc:
            return jsonify({"message": "dni_ruc no puede ser vacío"}), 400
        if len(dni_ruc) in (8, 11) and not dni_ruc.isdigit():
            return jsonify({"message": "dni_ruc inválido (debe ser numérico si es DNI/RUC)"}), 400
        updates["dni_ruc"] = dni_ruc

    if "nombre_razon_social" in updates:
        nombre = (updates["nombre_razon_social"] or "").strip()
        if not nombre:
            return jsonify({"message": "nombre_razon_social no puede ser vacío"}), 400
        updates["nombre_razon_social"] = nombre

    set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
    params = list(updates.values()) + [cliente_id]

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    UPDATE cliente
                    SET {set_clause}
                    WHERE cliente_id = %s;
                """, params)

                if cur.rowcount == 0:
                    return jsonify({"message": "Cliente no encontrado"}), 404

            conn.commit()

        return jsonify({"message": "Cliente actualizado", "cliente_id": cliente_id}), 200

    except Exception as e:
        return jsonify({"message": "No se pudo actualizar cliente", "error": str(e)}), 400


@clientes_bp.delete("/api/clientes/<int:cliente_id>")
def eliminar_cliente(cliente_id: int):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM cliente WHERE cliente_id = %s;", (cliente_id,))
                if cur.rowcount == 0:
                    return jsonify({"message": "Cliente no encontrado"}), 404
            conn.commit()

        return jsonify({"message": "Cliente eliminado", "cliente_id": cliente_id}), 200

    except Exception as e:
        return jsonify({"message": "No se pudo eliminar cliente", "error": str(e)}), 400
