import os
from flask import Flask, jsonify
from dotenv import load_dotenv

from db import get_conn

from routes.proveedores import proveedores_bp
from routes.clientes import clientes_bp



def create_app():
    load_dotenv()  # carga .env local (NO se sube a GitHub)

    app = Flask(__name__)

    @app.get("/api/health")
    def health():
        """
        Prueba de vida + prueba real de conexión a PostgreSQL.
        """
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1 AS ok;")
                    row = cur.fetchone()

            return jsonify({
                "status": "ok",
                "db": "connected",
                "check": row["ok"]
            }), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "db": "not_connected",
                "message": str(e)
            }), 500
        
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(clientes_bp)



    return app

if __name__ == "__main__":
    app = create_app()
    # host 0.0.0.0 para que sea accesible (también útil si luego dockerizo el backend)
    app.run(host="0.0.0.0", port=5000, debug=True)
