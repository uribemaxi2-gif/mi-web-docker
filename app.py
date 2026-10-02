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
    <title>Mi primera web usando docker.... me adelanto a vo nuevo de la villaaa</title>
</head>
<body>
    <h1>Mi app con PostgreSQL</h1>

    <form method="POST">
        <input
            type="text"
            name="nota"
            placeholder="Escribe una nota"
            maxlength="200"
            required
        >
        <button type="submit">Guardar</button>
    </form>

    <h2>NOTAS O TIPS</h2>

    <ul>
        {% for nota in notas %}
            <li>{{ nota }}</li>
        {% endfor %}
    </ul>
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
