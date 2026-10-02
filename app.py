import os 
import psycopg

from flask import Flask, request, redirect, url_for , render_template_string

app = Flask(__name__)

#PostgreSQL
DB_CONFIG = {
    "host": os.environ["DB_HOST"],
    "dbname": os.environ["POSTGRES_DB"],
    "user": os.environ["POSTGRES_USER"],
    "password": os.environ["POSTGRES_PASSWORD"]
}

#pagina en HTML
HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notas y Tips | App con PostgreSQL</title>
    <style>
        :root {
            --bg: #f4f6fb;
            --card: #ffffff;
            --text: #1f2937;
            --muted: #6b7280;
            --primary: #4f46e5;
            --primary-dark: #4338ca;
            --border: #e5e7eb;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.5;
            min-height: 100vh;
        }

        header {
            background: linear-gradient(135deg, var(--primary), #7c3aed);
            color: #fff;
            padding: 40px 20px;
            text-align: center;
        }

        header h1 { font-size: 1.9rem; font-weight: 700; }
        header p { margin-top: 6px; opacity: 0.85; font-size: 0.95rem; }

        main {
            max-width: 680px;
            margin: -24px auto 40px;
            padding: 0 16px;
        }

        .card {
            background: var(--card);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.07);
        }

        .card h2 {
            font-size: 1.1rem;
            margin-bottom: 16px;
        }

        form { display: flex; gap: 10px; }

        input[type="text"] {
            flex: 1;
            padding: 12px 14px;
            font-size: 1rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        input[type="text"]:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
        }

        button {
            padding: 12px 22px;
            font-size: 1rem;
            font-weight: 600;
            color: #fff;
            background: var(--primary);
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
        }

        button:hover { background: var(--primary-dark); }

        ul { list-style: none; }

        li {
            padding: 12px 14px;
            border-left: 4px solid var(--primary);
            background: #f9fafb;
            border-radius: 6px;
            margin-bottom: 10px;
            word-break: break-word;
        }

        li:last-child { margin-bottom: 0; }

        .empty {
            text-align: center;
            color: var(--muted);
            padding: 16px 0;
        }

        footer {
            text-align: center;
            color: var(--muted);
            font-size: 0.85rem;
            padding-bottom: 30px;
        }

        @media (max-width: 480px) {
            form { flex-direction: column; }
        }
    </style>
</head>
<body>
    <header>
        <h1>Mi app con PostgreSQL</h1>
        <p>Guarda y consulta tus notas de forma simple</p>
    </header>

    <main>
        <section class="card">
            <h2>Nueva nota</h2>
            <form method="POST">
                <input
                    type="text"
                    name="nota"
                    placeholder="Escribe una nota o tip"
                    maxlength="200"
                    required
                >
                <button type="submit">Guardar</button>
            </form>
        </section>

        <section class="card">
            <h2>Notas y tips</h2>
            {% if notas %}
                <ul>
                    {% for nota in notas %}
                        <li>{{ nota }}</li>
                    {% endfor %}
                </ul>
            {% else %}
                <p class="empty">Aún no hay notas. ¡Agrega la primera!</p>
            {% endif %}
        </section>
    </main>

    <footer>Flask · PostgreSQL · Docker</footer>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def inicio():

    # Cuando el usuario envía el formulario
    if request.method == "POST":

        nota = request.form.get("nota", "").strip()

        if nota and len(nota) <= 200:
            with psycopg.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO notas (contenido) VALUES (%s)",
                        (nota,)
                    )

        return redirect(url_for("inicio"))

    # Cuando el usuario simplemente visita la página (GET)
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT contenido FROM notas ORDER BY id DESC"
            )

            notas = [fila[0] for fila in cursor.fetchall()]

    return render_template_string(HTML, notas=notas)
