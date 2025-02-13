from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)

# Para SQLite (archivo local)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///equipos.db'

# Para MySQL (cambia los datos de conexión)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://usuario:contraseña@localhost/equipos_db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Definir el modelo de la base de datos
class Equipo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    piso = db.Column(db.String(10), nullable=False)
    maquina_actual = db.Column(db.String(50), nullable=False)
    version_windows = db.Column(db.String(20), nullable=False)
    usuario = db.Column(db.String(50), nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, nullable=True)
    maquina_anterior = db.Column(db.String(50), nullable=True)
    edificio = db.Column(db.String(100), nullable=True) 

# Crear la base de datos y las tablas si no existen
with app.app_context():
    db.create_all()

# Página principal con la lista de equipos filtrado
@app.route('/', methods=['GET'])
def index():
    filtro = request.args.get('filtro', '')
    valor = request.args.get('valor', '')
    filtro_edificio = request.args.get('edificio', '')
    filtro_piso = request.args.get('piso', '')
    filtro_version = request.args.get('version_windows', '')

    # Construimos la consulta base
    consulta = Equipo.query

    # Filtrar por edificio
    if filtro_edificio:
        consulta = consulta.filter(Equipo.edificio == filtro_edificio)
        if filtro_piso:  # Si también se selecciona un piso
            consulta = consulta.filter(Equipo.piso == filtro_piso)

    if filtro_version:
        consulta = consulta.filter(Equipo.version_windows == filtro_version)
    
    if filtro and valor:
        if filtro == 'piso':
            consulta = consulta.filter(Equipo.piso.contains(valor))
        elif filtro == 'maquina_actual':
            consulta = consulta.filter(Equipo.maquina_actual.contains(valor))
        elif filtro == 'usuario':
            consulta = consulta.filter(Equipo.usuario.contains(valor))

    equipos = consulta.all()
    return render_template('index.html', equipos=equipos, filtro=filtro, valor=valor, filtro_version=filtro_version, filtro_edificio=filtro_edificio, filtro_piso=filtro_piso)


# Ruta para agregar un equipo
@app.route('/agregar', methods=['POST'])
def agregar():
    edificio = request.form['edificio']
    piso = request.form['piso']
    maquina_actual = request.form['maquina_actual']
    version_windows = request.form['version_windows']
    usuario = request.form['usuario']
    maquina_anterior = request.form['maquina_anterior']

    fecha_actualizacion = request.form['fecha_actualizacion']
    fecha_actualizacion = datetime.strptime(fecha_actualizacion, '%Y-%m-%dT%H:%M') if fecha_actualizacion else None

    nuevo_equipo = Equipo(
        edificio=edificio,
        piso=piso, 
        maquina_actual=maquina_actual, 
        version_windows=version_windows, 
        usuario=usuario, 
        fecha_actualizacion=fecha_actualizacion,
        maquina_anterior=maquina_anterior if maquina_anterior else None
    )

    db.session.add(nuevo_equipo)
    db.session.commit()
    return redirect('/')

# Ruta para eliminar un equipo
@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    equipo = Equipo.query.get(id)
    if equipo:
        db.session.delete(equipo)
        db.session.commit()
    return redirect('/')

# Ruta para cargar la página de edición
@app.route('/editar/<int:id>', methods=['GET'])
def editar(id):
    equipo = Equipo.query.get(id)
    return render_template('editar.html', equipo=equipo)

# Ruta para actualizar un equipo
@app.route('/actualizar/<int:id>', methods=['POST'])
def actualizar(id):
    equipo = Equipo.query.get(id)

    equipo.edificio = request.form['edificio']
    equipo.piso = request.form['piso']
    equipo.maquina_actual = request.form['maquina_actual']
    equipo.version_windows = request.form['version_windows']
    equipo.usuario = request.form['usuario']
    equipo.maquina_anterior = request.form['maquina_anterior'] if request.form['maquina_anterior'] else None

    equipo.fecha_actualizacion = request.form['fecha_actualizacion']
    equipo.fecha_actualizacion = datetime.strptime(equipo.fecha_actualizacion, '%Y-%m-%dT%H:%M') if equipo.fecha_actualizacion else None

    print(str(equipo)) 
    db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    #app.run(ssl_context=('cert/cert.pem', 'cert/key.pem'), debug=True, port=443)
    app.run(host="0.0.0.0", port=5000, debug=True)  # NO usamos ssl_context
