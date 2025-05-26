from flask import Blueprint, request, render_template, redirect, current_app
from flask_login import login_required, current_user
from models import db, ReclamosBangho
from .logs import logger
from datetime import date

reclamos_b_bp = Blueprint('reclamos_b', __name__)

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

@reclamos_b_bp.route('/reclamos_b', methods=['GET'])
@login_required
def reclamos_b():
    filtro = request.args.get('filtro', '')
    valor = request.args.get('valor', '')
    filtro_edificio = request.args.get('edificio', '')
    filtro_piso = request.args.get('piso', '')
    filtro_estado_reclamos = request.args.get('estado_r', '')

    # Construimos la consulta base
    consulta = ReclamosBangho.query

    # Filtrar por edificio
    if filtro_edificio:
        consulta = consulta.filter(ReclamosBangho.edificio == filtro_edificio)
        if filtro_piso:  # Si también se selecciona un piso
            consulta = consulta.filter(ReclamosBangho.piso == filtro_piso)

    if filtro_estado_reclamos:
        consulta = consulta.filter(ReclamosBangho.estado == filtro_estado_reclamos)

    if filtro and valor:
        if filtro == 'numero_serie':
            consulta = consulta.filter(ReclamosBangho.numero_serie.contains(valor))
        elif filtro == 'asunto':
            consulta = consulta.filter(ReclamosBangho.asunto.contains(valor))

    reclamos = consulta.all()
    return render_template('reclamos_b.html', reclamos=reclamos, filtro=filtro, valor=valor, filtro_estado_reclamos=filtro_estado_reclamos, filtro_edificio=filtro_edificio, filtro_piso=filtro_piso)

@reclamos_b_bp.route('/agregar_reclamo_b', methods=['GET','POST'])
@login_required
def agregar_reclamo_b():
    if request.method == 'POST':
        try:
            form_data = {
                'numero_serie': request.form.get('numero_serie', '').strip(),
                'asunto': request.form.get('asunto', '').strip(),
                'numero_referencia': request.form.get('numero_referencia', '').strip(),
                'estado': request.form.get('estado', '').strip(),
                'edificio': request.form.get('edificio', '').strip(),
                'piso': request.form.get('piso', '').strip(),
                'descripcion': request.form.get('descripcion', '').strip(),
                'tarea_realizada': request.form.get('tarea_realizada', '').strip(),
                'equipo_utilizado': request.form.get('equipo_utilizado', '').strip(),
                'fecha': request.form.get('fecha', '').strip()
            }

            fecha = date.fromisoformat(form_data['fecha']) if form_data['fecha'] else None

            reclamo_existente = ReclamosBangho.query.filter_by(numero_referencia=form_data['numero_referencia']).first()
            if reclamo_existente:
                log_data = {
                    'numero_referencia': form_data['numero_referencia'],
                    'intento': form_data,
                    'mensaje': 'Reclamo ya existe en la base de datos'
                }
                safe_log('conflict', 'reclamo_b', log_data, current_user.username)
                return """
                <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
                <script>
                    document.addEventListener("DOMContentLoaded", function() {
                        Swal.fire({
                            title: 'Error',
                            text: 'El número de referencia ya existe.',
                            icon: 'error',
                            confirmButtonText: 'Aceptar'
                        }).then(() => {
                            window.opener.location.reload();  // Recargar la página principal
                            window.close();
                        });
                    });
                </script>
                """
            
            nuevo_reclamo_b = ReclamosBangho(
                numero_serie=form_data['numero_serie'],
                asunto=form_data['asunto'], 
                numero_referencia=form_data['numero_referencia'],
                estado=form_data['estado'], 
                fecha=fecha,
                edificio=form_data['edificio'],
                piso=form_data['piso'],
                descripcion=form_data['descripcion'] or None,
                tarea_realizada=form_data['tarea_realizada'] or None,
                equipo_utilizado=form_data['equipo_utilizado'] or None
            )

            db.session.add(nuevo_reclamo_b)
            db.session.commit()

            safe_log(
                action='create',
                entity='reclamo_b',
                details={
                    'id': nuevo_reclamo_b.id,
                    'numero_serie': nuevo_reclamo_b.numero_serie,
                    'asunto': nuevo_reclamo_b.asunto,
                    'numero_referencia': nuevo_reclamo_b.numero_referencia,
                    'estado': nuevo_reclamo_b.estado,
                    'fecha': nuevo_reclamo_b.fecha,
                    'edificio': nuevo_reclamo_b.edificio,
                    'piso': nuevo_reclamo_b.piso,
                    'descripcion': nuevo_reclamo_b.descripcion,
                    'tarea_realizada': nuevo_reclamo_b.tarea_realizada,
                    'equipo_utilizado': nuevo_reclamo_b.equipo_utilizado
                },
                user=current_user.username
            )

            return """
            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    Swal.fire({
                        title: 'Un Éxito',
                        text: 'Reclamo agregado correctamente.',
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
            
            current_app.logger.error(f"Error en agregar_reclamo_b: {str(e)}")
            safe_log(
                action='error',
                entity='reclamo_b',
                details={'error': str(e), 'operacion': 'agregar_reclamo_b'},
                user=current_user.username
            )

            return """
            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    Swal.fire({
                        title: 'Error',
                        text: 'Ocurrió un error al agregar el reclamo.',
                        icon: 'error',
                        confirmButtonText: 'Aceptar'
                    }).then(() => {
                        window.opener.location.reload();
                        window.close();
                    });
                });
            </script>
            """
        
    return render_template('agregar_reclamo_b.html')

@reclamos_b_bp.route('/eliminar_reclamo_b/<int:id>', methods=['POST'])
@login_required
def eliminar_reclamo_b(id):
    try:
        reclamob = ReclamosBangho.query.get(id)

        safe_log(
            action='delete',
            entity='reclamo_b',
            details={
                'id': id,
                'numero_serie': reclamob.numero_serie,
                'asunto': reclamob.asunto,
                'numero_referencia': reclamob.numero_referencia,
                'estado': reclamob.estado,
                'fecha': reclamob.fecha,
                'edificio': reclamob.edificio,
                'piso': reclamob.piso,
                'descripcion': reclamob.descripcion,
                'tarea_realizada': reclamob.tarea_realizada,
                'equipo_utilizado': reclamob.equipo_utilizado
            },
            user=current_user.username
        )

        db.session.delete(reclamob)
        db.session.commit()

        return redirect('/reclamos_b')
    
    except Exception as e:
        db.session.rollback()
        safe_log(
            action='error',
            entity='reclamo_b',
            details={
                'operation': 'delete',
                'error': str(e),
                'reclamo_b_id': id
            },
            user=current_user.username
        )
        return "Error al eliminar el reclamo", 500

@reclamos_b_bp.route('/editar_reclamo_b/<int:id>', methods=['GET'])
@login_required
def editar_reclamo_b(id):
    reclamob = ReclamosBangho.query.get(id)
    return render_template('editar_reclamo_b.html', reclamob=reclamob)

@reclamos_b_bp.route('/actualizar_reclamo_b/<int:id>', methods=['POST'])
@login_required
def actualizar_reclamo_b(id):
    reclamob = ReclamosBangho.query.get(id)

    if request.method == 'POST':
        try:
            datos_antiguos = {
                'numero_serie': reclamob.numero_serie,
                'asunto': reclamob.asunto,
                'numero_referencia': reclamob.numero_referencia,
                'estado': reclamob.estado,
                'fecha': reclamob.fecha,
                'edificio': reclamob.edificio,
                'piso': reclamob.piso,
                'descripcion': reclamob.descripcion,
                'tarea_realizada': reclamob.tarea_realizada,
                'equipo_utilizado': reclamob.equipo_utilizado
            }

            reclamob.numero_serie = request.form['numero_serie']
            reclamob.asunto = request.form['asunto']
            reclamob.numero_referencia = request.form['numero_referencia']
            reclamob.estado = request.form['estado']
            reclamob.edificio=request.form['edificio']
            reclamob.piso=request.form['piso']
            reclamob.descripcion = request.form['descripcion']
            reclamob.tarea_realizada = request.form['tarea_realizada']
            reclamob.equipo_utilizado = request.form['equipo_utilizado']

            reclamob.fecha_str = request.form['fecha']

            if reclamob.fecha_str:
                reclamob.fecha = date.fromisoformat(reclamob.fecha_str)
            else:
                reclamob.fecha = None  # Si el campo está vacío, guarda NULL en la base de datos

            db.session.commit()

            safe_log(
                action='update',
                entity='reclamo_b',
                details={
                    'id': id,
                    'cambios': {
                        'antes': datos_antiguos,
                        'despues': {
                            'numero_serie': reclamob.numero_serie,
                            'asunto': reclamob.asunto,
                            'numero_referencia': reclamob.numero_referencia,
                            'estado': reclamob.estado,
                            'fecha': reclamob.fecha,
                            'edificio': reclamob.edificio,
                            'piso': reclamob.piso,
                            'descripcion': reclamob.descripcion,
                            'tarea_realizada': reclamob.tarea_realizada,
                            'equipo_utilizado': reclamob.equipo_utilizado
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
                        text: 'Reclamo actualizado correctamente.',
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
                entity='reclamo_b',
                details={
                    'operation': 'delete',
                    'error': str(e),
                    'reclamo_b_id': id
                },
                user=current_user.username
            )
            return "Error al eliminar el reclamo", 500

    return redirect('/reclamos_b')