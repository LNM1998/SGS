from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin
from sqlalchemy import Boolean
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="10.10.10.6",
        user="ticketmanager",
        password="Enacom18",
        database="glpi"
    )

db = SQLAlchemy()

migrate = Migrate()

def init_db(app):
    
    # Configuración de la base de datos
    app.config['SECRET_KEY'] = '2ab924184b6669d0086018a2ff24550ee94643244ca1c57f'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///equipos.db'  # Para SQLite
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://usuario:contraseña@localhost/equipos_db'  # Para MySQL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa las extensiones con la aplicación
    db.init_app(app)
    migrate.init_app(app, db)

    # Crea la base de datos y las tablas si no existen
    with app.app_context():
        db.create_all()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='lectura')  # Nueva columna
    is_admin = db.Column(db.Boolean, default=False)  # Indica si el usuario es administrador
    is_active = db.Column(db.Boolean, default=True)  # Indica si el usuario está activo
    nombre_usuario = db.Column(db.String(30), nullable=True)
    apellido_usuario = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(50), nullable=True)

    # Método para verificar permisos
    def has_role(self, *roles):
        return self.role in roles

    def __repr__(self):
        return f'<User {self.username}>'
    
# Definir el modelo de la base de datos
class Equipo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    piso = db.Column(db.String(10), nullable=False)
    maquina_actual = db.Column(db.String(50), nullable=False)
    version_windows = db.Column(db.String(20), nullable=False)
    usuario = db.Column(db.String(50), nullable=False)
    fecha_actualizacion = db.Column(db.Date, nullable=True)
    maquina_anterior = db.Column(db.String(50), nullable=True)
    edificio = db.Column(db.String(100), nullable=True)
    nombre_usuario = db.Column(db.String(30), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    numero_serie = db.Column(db.String(50), nullable=True, default='SIN_NUMERO')

class ReclamosBangho(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero_serie = db.Column(db.String(50), nullable=False)
    asunto = db.Column(db.String(50), nullable=False)
    numero_referencia = db.Column(db.String(15), nullable=False, unique=True)  # Formato 000000-000000
    estado = db.Column(db.Enum('sin responder', 'en espera', 'resuelto'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    edificio = db.Column(db.String(100), nullable=False)
    piso = db.Column(db.String(10), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    tarea_realizada = db.Column(db.Text, nullable=True)
    equipo_utilizado = db.Column(db.String(50), nullable=True)

class ReclamosExternal(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero_serie = db.Column(db.String(50), nullable=False)
    asunto = db.Column(db.String(50), nullable=False)
    numero_referencia = db.Column(db.String(15), nullable=True, unique=False)  # Formato 000000-000000
    estado = db.Column(db.Enum('sin responder', 'en espera', 'resuelto'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    edificio = db.Column(db.String(100), nullable=False)
    piso = db.Column(db.String(10), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    tarea_realizada = db.Column(db.Text, nullable=True)
    contador = db.Column(db.String(50), nullable=True)

class Notebook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.Enum('dell i5', 'dell i7', 'dell i7 diseno', 'exo i5', 'exo i7'), nullable=False)
    inventario = db.Column(db.String(20), nullable=False)
    numero_serie = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.Enum('fisica', 'asignada', 'no devuelta', 'rota', 'robada', 'perdida'), nullable=False)
    usuario = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.Date, nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    archivo_notebook = db.Column(db.String(200), nullable=True)
    archivo_pdf = db.Column(db.String(200), nullable=True)

class Impresora(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    numero_serie = db.Column(db.String(50), nullable=False)
    alquilada = db.Column(Boolean, nullable=False)
    edificio = db.Column(db.String(50), nullable=False)
    piso = db.Column(db.String(10), nullable=False)
    servidor = db.Column(db.String(50), nullable=True)
    ip = db.Column(db.String(50), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)

class Remito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo_remito = db.Column(db.String(50), nullable=False)
    remitente = db.Column(db.String(50), nullable=False)
    destinatario = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    observacion = db.Column(db.String(200))
    estado = db.Column(db.String(50), nullable=False)
    archivo_remito = db.Column(db.String(200))
    articulos = db.relationship('ArticuloRemito', backref='remito', lazy=True)  # Relación con los artículos

class ArticuloRemito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    remito_id = db.Column(db.Integer, db.ForeignKey('remito.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    numero_serie = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(50), nullable=False)
    observacion = db.Column(db.String(200))

class Hardware(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    inventario = db.Column(db.String(20), nullable=True)
    numero_serie = db.Column(db.String(50), nullable=True)
    edificio = db.Column(db.String(100), nullable=False)
    piso = db.Column(db.String(10), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    usuario = db.Column(db.String(20), nullable=True)

class Proveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(30), nullable=False)
    telefono = db.Column(db.String(30), nullable=False)
    celular = db.Column(db.String(30), nullable=False)
    pagina = db.Column(db.String(50), nullable=False)
    observacion = db.Column(db.String(100), nullable=False)
    latitud = db.Column(db.String(30), nullable=True)
    longitud = db.Column(db.String(30), nullable=True)
    direccion = db.Column(db.String(50), nullable=False)