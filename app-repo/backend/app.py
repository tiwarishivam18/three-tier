import os
import time
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "postgres-service")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "userdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres123")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def init_db():
    retries = 20
    while retries > 0:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS personal_details (
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    email VARCHAR(150) NOT NULL,
                    phone VARCHAR(30) NOT NULL,
                    address TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            print("Database initialized successfully.")
            return
        except Exception as exc:
            print(f"Database not ready yet: {exc}")
            retries -= 1
            time.sleep(5)

    raise Exception("Could not connect to database after multiple retries.")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "backend"}), 200


@app.route("/submit", methods=["POST"])
def submit():
    try:
        data = request.get_json()

        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        phone = data.get("phone")
        address = data.get("address")

        if not all([first_name, last_name, email, phone, address]):
            return jsonify({"error": "All fields are required"}), 400

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO personal_details (first_name, last_name, email, phone, address)
            VALUES (%s, %s, %s, %s, %s)
        """, (first_name, last_name, email, phone, address))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Personal details saved successfully"}), 201

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/records", methods=["GET"])
def records():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, first_name, last_name, email, phone, address, created_at
            FROM personal_details
            ORDER BY id DESC
        """)
        rows = cur.fetchall()

        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "phone": row[4],
                "address": row[5],
                "created_at": str(row[6])
            })

        cur.close()
        conn.close()

        return jsonify(result), 200

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
else:
    init_db()