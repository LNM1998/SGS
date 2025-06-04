from flask import Blueprint, request, render_template, redirect, current_app
from flask_login import login_required, current_user
from models import db, ReclamosExternal
from .logs import logger
from datetime import date

reclamos_e_bp = Blueprint('reclamos_e', __name__)

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

@reclamos_e_bp.route('/reclamos_e', methods=['GET'])
@login_required
def reclamos_e():
    filtro = request.args.get('filtro', '')
    valor = request.args.get('valor', '')
    filtro_edificio = request.args.get('edificio', '')
    filtro_piso = request.args.get('piso', '')
    filtro_estado_reclamos = request.args.get('estado_r', '')

    # Construimos la consulta base
    consulta = ReclamosExternal.query

    # Filtrar por edificio
    if filtro_edificio:
        consulta = consulta.filter(ReclamosExternal.edificio == filtro_edificio)
        if filtro_piso:  # Si también se selecciona un piso
            consulta = consulta.filter(ReclamosExternal.piso == filtro_piso)

    if filtro_estado_reclamos:
        consulta = consulta.filter(ReclamosExternal.estado == filtro_estado_reclamos)

    if filtro and valor:
        # if filtro == 'piso':
        #     consulta = consulta.filter(ReclamosExternal.piso.contains(valor))
        if filtro == 'numero_serie':
            consulta = consulta.filter(ReclamosExternal.numero_serie.contains(valor))
        elif filtro == 'asunto':
            consulta = consulta.filter(ReclamosExternal.asunto.contains(valor))

    reclamos = consulta.all()
    return render_template('reclamos_e.html', reclamos=reclamos, filtro=filtro, valor=valor, filtro_estado_reclamos=filtro_estado_reclamos, filtro_edificio=filtro_edificio, filtro_piso=filtro_piso)

@reclamos_e_bp.route('/agregar_reclamo_e', methods=['GET','POST'])
@login_required
def agregar_reclamo_e():
    if request.method == 'POST':
        try:
            form_data = {
                'numero_serie' : request.form.get('numero_serie', '').strip(),
                'asunto' : request.form.get('asunto', '').strip(),
                'numero_referencia' : request.form.get('numero_referencia', '').strip(),
                'estado' : request.form.get('estado', '').strip(),
                'edificio' : request.form.get('edificio', '').strip(),
                'piso' : request.form.get('piso', '').strip(),
                'descripcion' : request.form.get('descripcion', '').strip(),
                'tarea_realizada' : request.form.get('tarea_realizada', '').strip(),
                'contador' : request.form.get('contador').strip(),
                'fecha' : request.form.get('fecha', '').strip(),
            }

            fecha = date.fromisoformat(form_data['fecha']) if form_data['fecha'] else None

            nuevo_reclamo_e = ReclamosExternal(
                numero_serie=form_data['numero_serie'],
                asunto=form_data['asunto'], 
                numero_referencia=form_data['numero_referencia'], 
                estado=form_data['estado'], 
                fecha=fecha,
                edificio=form_data['edificio'],
                piso=form_data['piso'],
                descripcion=form_data['descripcion'] or None,
                tarea_realizada=form_data['tarea_realizada'] or None,
                contador=form_data['contador']
            )

            db.session.add(nuevo_reclamo_e)
            db.session.commit()

            safe_log(
                action='create',
                entity='reclamo_e',
                details={
                    'id': nuevo_reclamo_e.id,
                    'numero_serie' : nuevo_reclamo_e.numero_serie,
                    'asunto' : nuevo_reclamo_e.asunto,
                    'numero_referencia' : nuevo_reclamo_e.numero_referencia,
                    'estado' : nuevo_reclamo_e.estado,
                    'fecha' : nuevo_reclamo_e.fecha,
                    'edificio' : nuevo_reclamo_e.edificio,
                    'piso' : nuevo_reclamo_e.piso,
                    'descripcion' : nuevo_reclamo_e.descripcion,
                    'tarea_realizada' : nuevo_reclamo_e.tarea_realizada,
                    'contador' : nuevo_reclamo_e.contador
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
            
            current_app.logger.error(f"Error en agregar_reclamo_e: {str(e)}")
            safe_log(
                action='error',
                entity='reclamo_e',
                details={'error': str(e), 'operacion': 'agregar_reclamo_e'},
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
    return render_template('agregar_reclamo_e.html')

@reclamos_e_bp.route('/eliminar_reclamo_e/<int:id>', methods=['POST'])
@login_required
def eliminar_reclamo_e(id):
    try:
        reclamoe = ReclamosExternal.query.get(id)

        safe_log(
            action='delete',
            entity='reclamo_e',
            details={
                'id': id,
                'numero_serie' : reclamoe.numero_serie,
                'asunto' : reclamoe.asunto,
                'numero_referencia' : reclamoe.numero_referencia,
                'estado' : reclamoe.estado,
                'fecha' : reclamoe.fecha,
                'edificio' : reclamoe.edificio,
                'piso' : reclamoe.piso,
                'descripcion' : reclamoe.descripcion,
                'tarea_realizada' : reclamoe.tarea_realizada,
                'contador' : reclamoe.contador
            },
            user=current_user.username
        )

        db.session.delete(reclamoe)
        db.session.commit()

        return redirect('/reclamos_e')
    
    except Exception as e:
        db.session.rollback()
        safe_log(
            action='error',
            entity='reclamo_e',
            details={
                'operation': 'delete',
                'error': str(e),
                'reclamo_b_id': id
            },
            user=current_user.username
        )
        return "Error al eliminar el reclamo", 500

@reclamos_e_bp.route('/editar_reclamo_e/<int:id>', methods=['GET'])
@login_required
def editar_reclamo_e(id):
    reclamoe = ReclamosExternal.query.get(id)
    return render_template('editar_reclamo_e.html', reclamoe=reclamoe)

@reclamos_e_bp.route('/actualizar_reclamo_e/<int:id>', methods=['POST'])
@login_required
def actualizar_reclamo_e(id):
    reclamoe = ReclamosExternal.query.get(id)

    if request.method == 'POST':
        try:
            datos_antiguos = {
                'numero_serie' : reclamoe.numero_serie,
                'asunto' : reclamoe.asunto,
                'numero_referencia' : reclamoe.numero_referencia,
                'estado' : reclamoe.estado,
                'fecha' : reclamoe.fecha,
                'edificio' : reclamoe.edificio,
                'piso' : reclamoe.piso,
                'descripcion' : reclamoe.descripcion,
                'tarea_realizada' : reclamoe.tarea_realizada,
                'contador' : reclamoe.contador
            }

            reclamoe.numero_serie = request.form['numero_serie']
            reclamoe.asunto = request.form['asunto']
            reclamoe.numero_referencia = request.form['numero_referencia']
            reclamoe.estado = request.form['estado']
            reclamoe.edificio=request.form['edificio']
            reclamoe.piso=request.form['piso']
            reclamoe.descripcion = request.form['descripcion']
            reclamoe.tarea_realizada = request.form['tarea_realizada']
            reclamoe.contador = request.form['contador']

            reclamoe.fecha_str = request.form['fecha']

            if reclamoe.fecha_str:
                reclamoe.fecha = date.fromisoformat(reclamoe.fecha_str)
            else:
                reclamoe.fecha = None  # Si el campo está vacío, guarda NULL en la base de datos

            db.session.commit()

            safe_log(
                action='update',
                entity='reclamo_e',
                details={
                    'id': id,
                    'cambios': {
                        'antes': datos_antiguos,
                        'despues': {
                            'numero_serie' : reclamoe.numero_serie,
                            'asunto' : reclamoe.asunto,
                            'numero_referencia' : reclamoe.numero_referencia,
                            'estado' : reclamoe.estado,
                            'fecha' : reclamoe.fecha,
                            'edificio' : reclamoe.edificio,
                            'piso' : reclamoe.piso,
                            'descripcion' : reclamoe.descripcion,
                            'tarea_realizada' : reclamoe.tarea_realizada,
                            'contador' : reclamoe.contador
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
                entity='reclamo_e',
                details={
                    'operation': 'delete',
                    'error': str(e),
                    'reclamo_e_id': id
                },
                user=current_user.username
            )
            return "Error al eliminar el reclamo", 500
        
    return redirect('/reclamos_e')