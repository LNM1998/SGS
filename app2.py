<<<<<<< HEAD
from flask import Flask, render_template, request, redirect, jsonify, Response, url_for, session, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import date, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from pathlib import Path
from models import db, init_db, User, Equipo, ReclamosBangho, ReclamosExternal, Notebook, Impresora, Hardware
from routes.forms import LoginForm, RegisterForm, CambiarRecuperarContraseñaForm, DataRequired
from routes.equipos import equipo_aios_bp
from routes.notebooks import notebooks_bp
from routes.impresoras import impresoras_bp
from routes.reclamos_b import reclamos_b_bp
from routes.reclamos_e import reclamos_e_bp
from routes.remitos import remitos_bp
from routes.documentacion import documentacion_bp
from routes.hardware import hardware_bp
from routes.proveedores import proveedores_bp
from routes.logs import logger
from sqlalchemy import not_
from models import get_db_connection
import pandas as pd
import io, json, re

app = Flask(__name__)

init_db(app)

logger.init_app(app)

app.register_blueprint(equipo_aios_bp)
app.register_blueprint(notebooks_bp)
app.register_blueprint(impresoras_bp)
app.register_blueprint(reclamos_b_bp)
app.register_blueprint(reclamos_e_bp)
app.register_blueprint(remitos_bp)
app.register_blueprint(documentacion_bp)
app.register_blueprint(hardware_bp)
app.register_blueprint(proveedores_bp)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    mensaje = None
    if form.validate_on_submit():
        session['username'] = form.username.data
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):  # Verificar el hash
            session['name'] = f"{user.nombre_usuario} {user.apellido_usuario}" 
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('index'))
        else:
            mensaje = 'Usuario o contraseña incorrectos'
    return render_template('login.html', form=form, mensaje=mensaje)

@app.route('/salir')
@login_required
def salir():
    logout_user()
    return redirect(url_for('login'))

@app.route('/registrar', methods=['GET', 'POST'])
@login_required
def registrar():
    mensaje = None
    if not current_user.is_admin:
        mensaje = 'Acceso Denegado'
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            password=generate_password_hash(form.password.data),
            nombre_usuario=form.name.data,
            apellido_usuario=form.lastname.data,
            email=form.email.data,
            is_admin=form.is_admin.data
        )
        db.session.add(user)
        db.session.commit()
        mensaje = 'Usuario registrado con éxito!'
        return redirect(url_for('index'))

    return render_template('register.html', form=form, mensaje=mensaje)
    
@app.route('/cambiar_contrasena', methods=['GET', 'POST'])
def cambiar_contrasena():
    form = CambiarRecuperarContraseñaForm()
    mensaje = None

    if current_user.is_authenticated:
        # Si sos admin y escribiste un username, blanqueás la clave de ese usuario
        if current_user.is_admin and request.method == 'POST' and request.form.get('username'):
            username_target = request.form.get('username')
            user = User.query.filter_by(username=username_target).first()
            if user:
                user.password = generate_password_hash(form.new_password.data)
                db.session.commit()
                mensaje = f"Contraseña blanqueada exitosamente para el usuario '{username_target}'"
            else:
                mensaje = "Usuario no encontrado"
        
        # Si no se especificó otro usuario, se cambia la contraseña del usuario logueado
        elif form.validate_on_submit():
            if check_password_hash(current_user.password, form.old_password.data):
                current_user.password = generate_password_hash(form.new_password.data)
                db.session.commit()
                mensaje = 'Contraseña cambiada con éxito'
                return redirect(url_for('index'))
            else:
                mensaje = 'Contraseña actual incorrecta'

        # Deshabilitar campo de usuario si no se está blanqueando
        if not current_user.is_admin:
            form.username.render_kw = {'disabled': 'disabled'}

    else:
        return redirect(url_for('login'))  # Redirigir a login si no está logueado

    return render_template('cambiar_contrasena.html', form=form, mensaje=mensaje)


@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    mensaje = None
    if not current_user.is_admin:
        mensaje = 'Acceso Denegado'
        return redirect(url_for('index'))

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        action = request.form.get('action')  # Verificar si es para dar o quitar admin
        new_role = request.form.get('new_role')
        user = User.query.get(user_id)

        if user:
            valid_roles = ['admin', 'basico', 'lectura']
            if new_role in valid_roles:
                user.role = new_role
                mensaje = f'Rol de {user.username} actualizado a {new_role}'
            if action == 'activate':
                user.is_active = True
                mensaje = f'{user.username} ha sido activado'
            elif action == 'deactivate':
                user.is_active = False
                mensaje = f'{user.username} ha sido desactivado'
            elif action == 'delete':
                db.session.delete(user)
                mensaje = f'{user.username} ha sido eliminado'
            
            db.session.commit()
        else:
            mensaje = 'Usuario no encontrado'

        return redirect(url_for('admin_dashboard'))

    users = User.query.all()

    return render_template('admin.html', users=users, mensaje=mensaje)

@app.route("/logs")
@login_required
def logs():
    LOG_FILE_PATH = Path("static/logs/system_operations.log")
    search_query = request.args.get("search", "").strip().lower()
    page = request.args.get("page", 1, type=int)
    logs_per_page = 10  # Número de líneas por página

    logs_list = []

    # Leer logs desde el archivo
    if LOG_FILE_PATH.exists():
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            all_logs = f.readlines()

        # Filtrar por búsqueda si hay un término ingresado
        if search_query:
            all_logs = [line for line in all_logs if search_query in line.lower()]

        # Paginar los logs
        total_logs = len(all_logs)
        start = (page - 1) * logs_per_page
        end = start + logs_per_page
        logs_list = all_logs[start:end]

        total_pages = (total_logs + logs_per_page - 1) // logs_per_page  # Redondeo hacia arriba
    else:
        logs_list = []
        total_pages = 1

    return render_template("logs.html", logs=logs_list, page=page, total_pages=total_pages, search_query=search_query)

@app.route('/descargar-logs')
def descargar_logs():
    log_path = "static/logs/system_operations.log"
    
    try:
        return send_file(log_path, as_attachment=True, download_name="system_operations.log")
    except Exception as e:
        return f"Error al descargar el archivo: {str(e)}", 500

@app.route('/calendario')
@login_required
def calendario():
    return render_template('calendario.html')

@app.route('/modificaciones_semanales')
@login_required
def modificaciones_semanales():
    desde = date.today() - timedelta(days=7)

    data = {
        'AIOS': Equipo.query.filter(Equipo.fecha_actualizacion >= desde).count() or 0,
        'Notebooks': Notebook.query.filter(Notebook.fecha >= desde).count() or 0,
        'ReclamosBangho': ReclamosBangho.query.filter(ReclamosBangho.fecha >= desde).count() or 0,
        'ReclamosExternal': ReclamosExternal.query.filter(ReclamosExternal.fecha >= desde).count() or 0,
    }

    return jsonify(data)

@app.route('/datos')
@login_required
def datos_grafico():
    # Contar registros de cada tabla
    total_aios = Equipo.query.count()
    total_notebooks = Notebook.query.count()
    total_impresoras = Impresora.query.count()
    total_reclamos_bangho = ReclamosBangho.query.count()
    total_reclamos_external = ReclamosExternal.query.count()

    # Enviar datos como JSON
    data = {
        "Equipos": {
            "AIOS": total_aios,
            "Notebooks": total_notebooks,
            "Impresoras": total_impresoras
        },
        "Reclamos": {
            "Bangho": total_reclamos_bangho,
            "External": total_reclamos_external
        }
    }
    return jsonify(data)

@app.route('/datos_tickets', methods=['POST'])
@login_required
def datos_tickets():
    fecha_inicio = request.form.get('fecha_inicio') or '2025-04-01'
    fecha_fin = request.form.get('fecha_fin') or '2025-04-24'

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT
          us.name AS tecnico_asignado,
          COUNT(t.id) AS cantidad_tickets
        FROM
          glpi_tickets t
          JOIN glpi_itilsolutions ts ON ts.items_id = t.id
          JOIN glpi_users us ON ts.users_id = us.id
        WHERE
          ts.users_id IN (
            '2187','2189','2178','2560','3161','3163','2186','2169','2982'
          )
          AND t.solvedate BETWEEN %s AND %s
        GROUP BY
          us.name
        ORDER BY
          cantidad_tickets DESC;
    """
    cursor.execute(query, (fecha_inicio, fecha_fin))
    resultados = cursor.fetchall()
    conn.close()

    labels = [row[0] for row in resultados]
    valores = [row[1] for row in resultados]

    return jsonify({"labels": labels, "valores": valores})

@app.route('/tickets', methods=['GET','POST'])
@login_required
def tickets():
    return render_template('datos_t.html')

def obtener_usuarios_anteriores(log_path):
    usuarios_anteriores = {}

    if not log_path.exists():
        return usuarios_anteriores

    with log_path.open('r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in reversed(lines):
        if '[UPDATE]' not in line or '[notebook]' not in line:
            continue

        id_match = re.search(r"'id':\s*(\d+)", line)
        if not id_match:
            continue
        notebook_id = int(id_match.group(1))

        if notebook_id in usuarios_anteriores:
            continue

        usuario_antes_match = re.search(r"'antes':.*?'usuario':\s*'([^']*)'", line)
        usuario_despues_match = re.search(r"'despues':.*?'usuario':\s*'([^']*)'", line)

        if usuario_antes_match and usuario_despues_match:
            usuario_antes = usuario_antes_match.group(1).strip()
            usuario_despues = usuario_despues_match.group(1).strip()

            if usuario_despues.lower() in ['', 'sin usuario', 'none']:
                usuarios_anteriores[notebook_id] = usuario_antes

    return usuarios_anteriores

@app.route('/index', methods=['GET'])
@login_required
def index():
    notebooks_recientes = (
        Notebook.query
        .filter(not_(Notebook.descripcion.ilike('%deshabilitado%')))
        .order_by(Notebook.fecha.desc())
        .limit(12)
        .all()
    )

    log_path = Path(app.root_path) / 'static' / 'logs' / 'system_operations.log'
    usuarios_anteriores = obtener_usuarios_anteriores(log_path)

    for nb in notebooks_recientes:
        setattr(nb, 'usuario_anterior', usuarios_anteriores.get(nb.id))

    return render_template('index.html', notebooks=notebooks_recientes)

@app.route('/exportar_excel/<tipo>')
@login_required
def exportar_excel(tipo):
    # Diccionario que mapea los tipos a los modelos
    modelos = {
        "equipos_aios": Equipo,
        "notebooks": Notebook,
        "impresoras": Impresora,
        "reclamos_bangho": ReclamosBangho,
        "reclamos_external": ReclamosExternal,
        "hardware": Hardware,
    }

    # Verificar si el tipo es válido
    if tipo not in modelos:
        return "Tipo no válido", 400

    # Definir las columnas que deseas exportar para cada tipo
    columnas_permitidas = {
        "equipos_aios": ["edificio", "piso", "maquina_actual", "numero_serie", "version_windows", "usuario", "fecha_actualizacion", "maquina_anterior"],
        "notebooks": ["modelo", "inventario", "numero_serie", "estado", "usuario", "direccion", "fecha", "descripcion"],
        "impresoras": ["nombre", "numero_serie", "es_alquilada", "edificio", "piso", "servidor", "ip", "descripcion"],
        "reclamos_bangho": ["numero_serie", "asunto", "numero_referencia", "estado", "fecha", "edificio", "piso", "descripcion", "tarea_realizada", "equipo_utilizado"],
        "reclamos_external": ["numero_serie", "asunto", "numero_referencia", "estado", "fecha", "edificio", "piso", "descripcion", "tarea_realizada", "contador"],
        "hardware": ["nombre", "inventario", "numero_serie", "descripcion", "edificio", "piso", "usuario"],
    }

    # Obtener parámetros de filtrado de la URL
=======
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

@app.route('/',  methods=['GET'])
def index():
    return render_template('index.html')

# Página principal con la lista de equipos filtrado
@app.route('/equipos_aios', methods=['GET'])
def equipos_aios():
>>>>>>> be0a8f4bcaeeadf7c4a7c2a8d4e19325df30310c
    filtro = request.args.get('filtro', '')
    valor = request.args.get('valor', '')
    filtro_edificio = request.args.get('edificio', '')
    filtro_piso = request.args.get('piso', '')
<<<<<<< HEAD
    filtro_estado_reclamos = request.args.get('estado_r', '')
    filtro_estado_notebook = request.args.get('estado', '')
    filtro_modelo = request.args.get('modelo', '')
    filtro_direccion = request.args.get('direccion', '')

    # Construir la consulta base
    consulta = modelos[tipo].query

    # Aplicar filtros
    if filtro_edificio:
        consulta = consulta.filter(modelos[tipo].edificio == filtro_edificio)
        if filtro_piso:
            consulta = consulta.filter(modelos[tipo].piso == filtro_piso)

    if filtro_estado_reclamos:
        consulta = consulta.filter(modelos[tipo].estado == filtro_estado_reclamos)

    if filtro_estado_notebook:
        consulta = consulta.filter(modelos[tipo].estado == filtro_estado_notebook)

    if filtro_modelo:
        consulta = consulta.filter(modelos[tipo].modelo == filtro_modelo)
    
    if filtro_direccion:
        consulta = consulta.filter(modelos[tipo].direccion == filtro_direccion)

    if filtro and valor:
        if filtro == 'maquina_actual':
            consulta = consulta.filter(modelos[tipo].maquina_actual.contains(valor))
        elif filtro == 'usuario':
            consulta = consulta.filter(modelos[tipo].usuario.contains(valor))
        elif filtro == 'numero_serie':
            consulta = consulta.filter(modelos[tipo].numero_serie.contains(valor))
        elif filtro == 'version_windows':
            consulta = consulta.filter(modelos[tipo].version_windows.contains(valor))
        elif filtro == 'asunto':
            consulta = consulta.filter(modelos[tipo].asunto.contains(valor))
        elif filtro == 'descripcion':
            consulta = consulta.filter(modelos[tipo].descripcion.contains(valor))
        elif filtro == 'ip':
            consulta = consulta.filter(modelos[tipo].ip.contains(valor))
        elif filtro == 'inventario':
            consulta = consulta.filter(modelos[tipo].inventario.contains(valor))  

    # Obtener los datos filtrados
    objetos = consulta.all()
    
    # Si no hay registros, devolver un mensaje
    if not objetos:
        return "No hay datos para exportar", 404

    # Convertir los datos a lista de diccionarios
    datos = [obj.__dict__ for obj in objetos]

    # Eliminar claves no necesarias (como _sa_instance_state de SQLAlchemy)
    for d in datos:
        d.pop("_sa_instance_state", None)

    # Filtrar solo las columnas permitidas
    datos_filtrados = [{col: d[col] for col in columnas_permitidas[tipo] if col in d} for d in datos]

    # Convertir a DataFrame de Pandas
    df = pd.DataFrame(datos_filtrados)

    # Crear un archivo en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=tipo.capitalize())

    output.seek(0)

    # Crear respuesta con el archivo
    response = Response(output.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response.headers["Content-Disposition"] = f"attachment; filename={tipo}.xlsx"

    return response

if __name__ == '__main__':
    #app.run(ssl_context=('cert/cert.pem', 'cert/key.pem'), debug=True, port=443)
    # app.run(host="0.0.0.0", port=5000, debug=True)  # NO usamos ssl_context
    app.run()
=======
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
    return render_template('equipos_aios.html', equipos=equipos, filtro=filtro, valor=valor, filtro_version=filtro_version, filtro_edificio=filtro_edificio, filtro_piso=filtro_piso)


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
    return redirect('/equipos_aios')

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

@app.route('/notebooks',  methods=['GET'])
def notebooks():
    return render_template('notebooks.html')

@app.route('/impresoras',  methods=['GET'])
def impresoras():
    return render_template('impresoras.html')

@app.route('/reclamos_b',  methods=['GET'])
def reclamos_b():
    return render_template('reclamos_b.html')

@app.route('/reclamos_e',  methods=['GET'])
def reclamos_e():
    return render_template('reclamos_e.html')

if __name__ == '__main__':
    #app.run(ssl_context=('cert/cert.pem', 'cert/key.pem'), debug=True, port=443)
    app.run(host="0.0.0.0", port=5000, debug=True)  # NO usamos ssl_context
>>>>>>> be0a8f4bcaeeadf7c4a7c2a8d4e19325df30310c
