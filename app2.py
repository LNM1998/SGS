from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# Configurar conexión a MySQL
db = mysql.connector.connect(
    host="localhost",
    port="3307",
    user="root",
    password="sqlroot",
    database="base_consultas"
)

@app.route('/')
def index():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, detalle FROM consultas")
    consultas = cursor.fetchall()
    cursor.close()
    return render_template("index.html", consultas=consultas)

@app.route('/buscar', methods=['POST'])
def buscar():
    texto_busqueda = request.form['busqueda'].lower()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, detalle FROM consultas WHERE LOWER(nombre) LIKE %s", (f"%{texto_busqueda}%",))
    resultados = cursor.fetchall()
    cursor.close()
    return render_template("index.html", consultas=resultados)

if __name__ == '__main__':
    app.run(ssl_context=('cert/cert.pem', 'cert/key.pem'), debug=True, port=443)
