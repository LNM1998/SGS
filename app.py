from flask import Flask, render_template, request

app = Flask(__name__)

# Datos simulados (en una app real, usarías una base de datos)
consultas = [
    {"id": 1, "nombre": "Consulta 1", "detalle": "Detalles de la consulta 1"},
    {"id": 2, "nombre": "Consulta 2", "detalle": "Detalles de la consulta 2"},
    {"id": 3, "nombre": "Consulta 3", "detalle": "Detalles de la consulta 3"},
]

@app.route('/')
def index():
    return render_template("index.html", consultas=consultas)

@app.route('/buscar', methods=['POST'])
def buscar():
    texto_busqueda = request.form['busqueda'].lower()
    resultados = [c for c in consultas if texto_busqueda in c["nombre"].lower()]
    return render_template("index.html", consultas=resultados)

if __name__ == '__main__':
    app.run(ssl_context=('cert/cert.pem', 'cert/key.pem'), debug=True, port=443)
