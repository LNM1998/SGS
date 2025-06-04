from flask import Blueprint, request, render_template, redirect, current_app
from flask_login import login_required, current_user
from models import db, Impresora
from .auth import lectura_allowed, basico_required
from .logs import logger
from datetime import date

impresoras_bp = Blueprint('impresoras', __name__)

def safe_log(action, entity, details, user=None):
    """Función de logging ultra-resistente a fallos"""
    try:
        user = user or (current_user.username if current_user.is_authenticated else 'system')
        details_str = str(details)

        current_app.logger.info(f"Intentando registrar log: {action}, {entity}, {details_str}, {user}")

        if hasattr(logger, 'is_initialized') and logger.is_initialized:
            logger.log(action, entity, details_str, user)
        else:
            current_app.logger.warning("Logger personalizado no inicializado")
    except Exception as e:
        current_app.logger.error(f"Fallo en safe_log: {str(e)}")

@impresoras_bp.route('/impresoras', methods=['GET'])
@login_required
@lectura_allowed
def impresoras():
    filtro = request.args.get('filtro', '')
    valor = request.args.get('valor', '')
    filtro_edificio = request.args.get('edificio', '')
    filtro_piso = request.args.get('piso', '')

    # Construimos la consulta base
    consulta = Impresora.query

    # Filtrar por edificio
    if filtro_edificio:
        consulta = consulta.filter(Impresora.edificio == filtro_edificio)
        if filtro_piso:  # Si también se selecciona un piso
            consulta = consulta.filter(Impresora.piso == filtro_piso)

    if filtro and valor:
        if filtro == 'ip':
            consulta = consulta.filter(Impresora.ip.contains(valor))
        elif filtro == 'numero_serie':
            consulta = consulta.filter(Impresora.numero_serie.contains(valor))

    impresoras = consulta.all()
    return render_template('impresoras.html', impresoras=impresoras, filtro=filtro, valor=valor, filtro_edificio=filtro_edificio, filtro_piso=filtro_piso)

@impresoras_bp.route('/agregar_impresora', methods=['GET','POST'])
@login_required
@basico_required
def agregar_impresora():
    if request.method == 'POST':
        try:
            form_data = {
                'nombre': request.form.get('nombre', '').strip(),
                'numero_serie': request.form.get('numero_serie', '').strip(),
                'edificio': request.form.get('edificio', '').strip(),
                'piso': request.form.get('piso', '').strip(),
                'servidor': request.form.get('servidor', '').strip(),
                'ip': request.form.get('ip', '').strip(),
                'descripcion': request.form.get('descripcion', '').strip(),
                'alquilada': bool(int(request.form.get("alquilada", 0)))
            }

            impresora_existente = Impresora.query.filter_by(numero_serie=form_data['numero_serie']).first()
            if impresora_existente:
                log_data = {
                    'numero_serie': form_data['numero_serie'],
                    'intento': form_data,
                    'mensaje': 'Impresora ya existe en la base de datos'
                }
                safe_log('conflict', 'impresora', log_data, current_user.username)
                return """
                <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
                <script>
                    document.addEventListener("DOMContentLoaded", function() {
                        Swal.fire({
                            title: 'Error',
                            text: 'El número de serie ya existe.',
                            icon: 'error',
                            confirmButtonText: 'Aceptar'
                        }).then(() => {
                            window.opener.location.reload();  // Recargar la página principal
                            window.close();
                        });
                    });
                </script>
                """

            nueva_impresora = Impresora(
                nombre=form_data['nombre'],
                numero_serie=form_data['numero_serie'],
                alquilada=form_data['alquilada'],
                edificio=form_data['edificio'],
                piso=form_data['piso'],
                servidor=form_data['servidor'],
                ip=form_data['ip'],
                descripcion=form_data['descripcion']
            )

            db.session.add(nueva_impresora)
            db.session.commit()

            safe_log(
                action='create',
                entity='impresora',
                details={
                    'id': nueva_impresora.id,
                    'nombre': nueva_impresora.nombre,
                    'numero_serie': nueva_impresora.numero_serie,
                    'edificio': nueva_impresora.edificio,
                    'piso': nueva_impresora.piso,
                    'servidor': nueva_impresora.servidor,
                    'ip': nueva_impresora.ip,
                    'descripcion': nueva_impresora.descripcion,
                    'alquilada': nueva_impresora.alquilada
                },
                user=current_user.username
            )
            return """
            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    Swal.fire({
                        title: 'Un Éxito',
                        text: 'Impresora agregada correctamente.',
                        icon: 'success',
                        confirmButtonText: 'Aceptar'
                    }).then(() => {
                        window.opener.location.reload();  // Recargar la página principal
                        window.close();  // Cerrar la ventana emergente
                    });
                });
            </script>
            """
        except Exception as e:
            db.session.rollback()
            
            current_app.logger.error(f"Error en agregar_impresora: {str(e)}")
            safe_log(
                action='error',
                entity='impresora',
                details={'error': str(e), 'operacion': 'agregar_impresora'},
                user=current_user.username
            )

            return """
            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    Swal.fire({
                        title: 'Error',
                        text: 'Ocurrió un error al agregar la impresora.',
                        icon: 'error',
                        confirmButtonText: 'Aceptar'
                    }).then(() => {
                        window.opener.location.reload();
                        window.close();
                    });
                });
            </script>
            """
    return render_template('agregar_impresora.html')

@impresoras_bp.route('/eliminar_impresora/<int:id>', methods=['POST'])
@login_required
@basico_required
def eliminar_impresora(id):
    try:
        impresora = Impresora.query.get(id)

        safe_log(
            action='delete',
            entity='impresora',
            details={
                'id': id,
                'nombre': impresora.nombre,
                'numero_serie': impresora.numero_serie,
                'edificio': impresora.edificio,
                'piso': impresora.piso,
                'servidor': impresora.servidor,
                'ip': impresora.ip,
                'descripcion': impresora.descripcion,
                'alquilada': impresora.alquilada
            },
            user=current_user.username
        )

        db.session.delete(impresora)
        db.session.commit()

        return redirect('/impresoras')
    
    except Exception as e:
        db.session.rollback()
        safe_log(
            action='error',
            entity='impresora',
            details={
                'operation': 'delete',
                'error': str(e),
                'impresora_id': id
            },
            user=current_user.username
        )
        return "Error al eliminar la impresora", 500

@impresoras_bp.route('/editar_impresora/<int:id>', methods=['GET'])
@login_required
@basico_required
def editar_impresora(id):
    impresora = Impresora.query.get(id)
    return render_template('editar_impresora.html', impresora=impresora)

@impresoras_bp.route('/actualizar_impresora/<int:id>', methods=['POST'])
@login_required
@basico_required
def actualizar_impresora(id):
    impresora = Impresora.query.get(id)
    
    if request.method == 'POST':
        try:
            datos_antiguos = {
                'nombre': impresora.nombre,
                'numero_serie': impresora.numero_serie,
                'edificio': impresora.edificio,
                'piso': impresora.piso,
                'servidor': impresora.servidor,
                'ip': impresora.ip,
                'descripcion': impresora.descripcion,
                'alquilada': impresora.alquilada
            }

            impresora.nombre = request.form['nombre']
            impresora.numero_serie = request.form['numero_serie']
            impresora.edificio = request.form['edificio']
            impresora.piso = request.form['piso']
            impresora.servidor = request.form['servidor']
            impresora.ip = request.form['ip']
            impresora.descripcion = request.form['descripcion']

            impresora.alquilada = request.form.get("alquilada")
            impresora.alquilada = bool(int(impresora.alquilada))  # Convierte "1" en True y "0" en False

            db.session.commit()

            safe_log(
                action='update',
                entity='impresora',
                details={
                    'id': id,
                    'cambios': {
                        'antes': datos_antiguos,
                        'despues': {
                            'nombre': impresora.nombre,
                            'numero_serie': impresora.numero_serie,
                            'edificio': impresora.edificio,
                            'piso': impresora.piso,
                            'servidor': impresora.servidor,
                            'ip': impresora.ip,
                            'descripcion': impresora.descripcion,
                            'alquilada': impresora.alquilada
                        }
                    }
                },
                user=current_user.username
            )

            return """
            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    Swal.fire({
                        title: 'Un Éxito',
                        text: 'Impresora actualizada correctamente.',
                        icon: 'success',
                        confirmButtonText: 'Aceptar'
                    }).then(() => {
                        window.opener.location.reload();  // Recargar la página principal
                        window.close();  // Cerrar la ventana emergente
                    });
                });
            </script>
            """
        except Exception as e:
            db.session.rollback()
            safe_log(
                action='error',
                entity='impresora',
                details={
                    'operation': 'delete',
                    'error': str(e),
                    'impresora_id': id
                },
                user=current_user.username
            )
            return "Error al eliminar la impresora", 500
        
    return redirect('/impresoras')