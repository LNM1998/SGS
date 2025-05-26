from flask import Blueprint, request, render_template, redirect, url_for, current_app
from flask_login import login_required, current_user
from pathlib import Path
from models import db, Equipo
from .auth import lectura_allowed, basico_required
from .logs import logger
from datetime import date

equipo_aios_bp = Blueprint('equipos', __name__)

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


@equipo_aios_bp.route('/equipos_aios', methods=['GET'])
@login_required
@lectura_allowed
def equipos_aios():
    filtro = request.args.get('filtro', '')
    valor = request.args.get('valor', '')
    filtro2 = request.args.get('filtro2', '')
    valor2 = request.args.get('valor2', '')
    filtro_edificio = request.args.get('edificio', '')
    filtro_piso = request.args.get('piso', '')
    filtro_version = request.args.get('version_windows', '')
    filtro_version2 = request.args.get('version_windows2', '')
    filtro_edificio2 = request.args.get('edificio2', '')
    filtro_piso2 = request.args.get('piso2', '')

    consulta = Equipo.query

    if filtro_edificio:
        consulta = consulta.filter(Equipo.edificio == filtro_edificio)
        if filtro_piso:
            consulta = consulta.filter(Equipo.piso == filtro_piso)

    if filtro_edificio2:
        consulta = consulta.filter(Equipo.edificio == filtro_edificio2)
        if filtro_piso2:
            consulta = consulta.filter(Equipo.piso == filtro_piso2)

    if filtro_version:
        consulta = consulta.filter(Equipo.version_windows == filtro_version)

    if filtro_version2:
        consulta = consulta.filter(Equipo.version_windows == filtro_version2)

    if filtro and valor:
        if filtro == 'maquina_actual':
            consulta = consulta.filter(Equipo.maquina_actual.contains(valor))
        elif filtro == 'numero_serie':
            consulta = consulta.filter(Equipo.numero_serie.contains(valor))
        elif filtro == 'usuario':
            consulta = consulta.filter(Equipo.usuario.contains(valor))
        elif filtro == 'descripcion':
            consulta = consulta.filter(Equipo.descripcion.contains(valor))

    if filtro2 and valor2:
        if filtro2 == 'maquina_actual':
            consulta = consulta.filter(Equipo.maquina_actual.contains(valor2))
        elif filtro2 == 'numero_serie':
            consulta = consulta.filter(Equipo.numero_serie.contains(valor2))
        elif filtro2 == 'usuario':
            consulta = consulta.filter(Equipo.usuario.contains(valor2))
        elif filtro2 == 'descripcion':
            consulta = consulta.filter(Equipo.descripcion.contains(valor2))

    equipos = consulta.all()
    return render_template('equipos_aios.html', equipos=equipos, filtro=filtro, valor=valor, filtro2=filtro2, valor2=valor2, filtro_version=filtro_version, filtro_edificio=filtro_edificio, filtro_piso=filtro_piso, filtro_version2=filtro_version2, filtro_edificio2=filtro_edificio2, filtro_piso2=filtro_piso2)

@equipo_aios_bp.route('/agregar_equipo', methods=['GET', 'POST'])
@login_required
@basico_required
def agregar_equipo():
    if request.method == 'POST':
        try:
            # Recoger datos del formulario
            form_data = {
                'edificio': request.form.get('edificio', '').strip(),
                'piso': request.form.get('piso', '').strip(),
                'maquina_actual': request.form.get('maquina_actual', '').strip(),
                'version_windows': request.form.get('version_windows', '').strip(),
                'usuario': request.form.get('usuario', '').strip(),
                'nombre_usuario': request.form.get('nombre_usuario', '').strip(),
                'maquina_anterior': request.form.get('maquina_anterior', '').strip(),
                'descripcion': request.form.get('descripcion', '').strip(),
                'numero_serie': request.form.get('numero_serie', '').strip(),
                'fecha_actualizacion': request.form.get('fecha_actualizacion', '').strip()
            }

            fecha_actualizacion = date.fromisoformat(form_data['fecha_actualizacion']) if form_data['fecha_actualizacion'] else None

            # Verificar si el equipo ya existe
            equipo_existente = Equipo.query.filter_by(maquina_actual=form_data['maquina_actual']).first()
            if equipo_existente:
                log_data = {
                    'maquina': form_data['maquina_actual'],
                    'intento': form_data,
                    'mensaje': 'Equipo ya existe en la base de datos'
                }
                safe_log('conflict', 'equipo', log_data, current_user.username)
                return """
                <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
                <script>
                    document.addEventListener("DOMContentLoaded", function() {
                        Swal.fire({
                            title: 'Error',
                            text: 'El número de máquina ya existe.',
                            icon: 'error',
                            confirmButtonText: 'Aceptar'
                        }).then(() => {
                            window.opener.location.reload();
                            window.close();
                        });
                    });
                </script>
                """

            # Crear nuevo equipo
            nuevo_equipo = Equipo(
                edificio=form_data['edificio'],
                piso=form_data['piso'],
                maquina_actual=form_data['maquina_actual'],
                version_windows=form_data['version_windows'],
                usuario=form_data['usuario'],
                nombre_usuario=form_data['nombre_usuario'] or None,
                fecha_actualizacion=fecha_actualizacion,
                maquina_anterior=form_data['maquina_anterior'] or None,
                descripcion=form_data['descripcion'] or None,
                numero_serie=form_data['numero_serie'] or None
            )

            db.session.add(nuevo_equipo)
            db.session.commit()

            safe_log(
                action='create',
                entity='equipo',
                details={
                    'id': nuevo_equipo.id,
                    'edificio': nuevo_equipo.edificio,
                    'piso': nuevo_equipo.piso,
                    'maquina': nuevo_equipo.maquina_actual,
                    'version_windows': nuevo_equipo.version_windows,
                    'usuario': nuevo_equipo.usuario,
                    'nombre_usuario': nuevo_equipo.nombre_usuario,
                    'maquina_anterior': nuevo_equipo.maquina_anterior,
                    'descripcion': nuevo_equipo.descripcion,
                    'numero_serie': nuevo_equipo.numero_serie,
                    'fecha_actualizacion': nuevo_equipo.fecha_actualizacion
                },
                user=current_user.username
            )

            return """
            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    Swal.fire({
                        title: 'Un Éxito',
                        text: 'PC agregada correctamente.',
                        icon: 'success',
                        confirmButtonText: 'Aceptar'
                    }).then(() => {
                        window.opener.location.reload();
                        window.close();
                    });
                });
            </script>
            """

        except Exception as e:
            db.session.rollback()
            
            current_app.logger.error(f"Error en agregar_equipo: {str(e)}")
            safe_log(
                action='error',
                entity='equipo',
                details={'error': str(e), 'operacion': 'agregar_equipo'},
                user=current_user.username
            )

            return """
            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    Swal.fire({
                        title: 'Error',
                        text: 'Ocurrió un error al agregar el equipo.',
                        icon: 'error',
                        confirmButtonText: 'Aceptar'
                    }).then(() => {
                        window.opener.location.reload();
                        window.close();
                    });
                });
            </script>
            """

    return render_template('agregar_equipo.html')

@equipo_aios_bp.route('/eliminar_equipo/<int:id>', methods=['POST'])
@login_required
@basico_required
def eliminar_equipo(id):
    try:
        equipo = Equipo.query.get_or_404(id)
        
        # Registrar datos antes de eliminar
        safe_log(
            action='delete',
            entity='equipo',
            details={
                'id': id,
                'edificio': equipo.edificio,
                'piso': equipo.piso,
                'maquina_actual': equipo.maquina_actual,
                'version_windows': equipo.version_windows,
                'nombre_usuario': equipo.nombre_usuario,
                'usuario': equipo.usuario,
                'maquina_anterior': equipo.maquina_anterior,
                'descripcion': equipo.descripcion,
                'numero_serie': equipo.numero_serie,
                'fecha_actualizacion': equipo.fecha_actualizacion
            },
            user=current_user.username
        )

        db.session.delete(equipo)
        db.session.commit()

        return redirect('/equipos_aios')
    
    except Exception as e:
        db.session.rollback()
        safe_log(
            action='error',
            entity='equipo',
            details={
                'operation': 'delete',
                'error': str(e),
                'equipo_id': id
            },
            user=current_user.username
        )
        return "Error al eliminar el equipo", 500

@equipo_aios_bp.route('/editar_equipo/<int:id>', methods=['GET'])
@login_required
@basico_required
def editar_equipo(id):
    equipo = Equipo.query.get(id)

    return render_template('editar_equipo.html', equipo=equipo)

@equipo_aios_bp.route('/actualizar_equipo/<int:id>', methods=['POST'])
@login_required
@basico_required
def actualizar_equipo(id):
    equipo = Equipo.query.get(id)

    if request.method == 'POST':
        try:
            # Capturar datos antiguos para el log
            datos_antiguos = {
                'edificio': equipo.edificio,
                'piso': equipo.piso,
                'maquina_actual': equipo.maquina_actual,
                'version_windows': equipo.version_windows,
                'nombre_usuario': equipo.nombre_usuario,
                'usuario': equipo.usuario,
                'maquina_anterior': equipo.maquina_anterior,
                'descripcion': equipo.descripcion,
                'numero_serie': equipo.numero_serie,
                'fecha_actualizacion': equipo.fecha_actualizacion
            }

            equipo.edificio = request.form['edificio']
            equipo.piso = request.form['piso']
            equipo.maquina_actual = request.form['maquina_actual']
            equipo.version_windows = request.form['version_windows']
            equipo.nombre_usuario = request.form['nombre_usuario'] if request.form['nombre_usuario'] else None
            equipo.usuario = request.form['usuario']
            equipo.maquina_anterior = request.form['maquina_anterior'] if request.form['maquina_anterior'] else None
            equipo.descripcion = request.form['descripcion'] if request.form['descripcion'] else None
            equipo.numero_serie = request.form['numero_serie'] if request.form['numero_serie'] else None

            equipo.fecha_actualizacion_str = request.form['fecha_actualizacion']

            if equipo.fecha_actualizacion_str:
                equipo.fecha_actualizacion = date.fromisoformat(equipo.fecha_actualizacion_str)
            else:
                equipo.fecha_actualizacion = None  # Si el campo está vacío, guarda NULL en la base de datos

            # Verificar si ya existe otro equipo con el mismo nombre de máquina
            equipo_existente = Equipo.query.filter_by(maquina_actual=equipo.maquina_actual).first()

            # Si existe y NO es el mismo ID (para evitar conflicto consigo mismo)
            if equipo_existente and equipo_existente.id != equipo.id:
                # Verificar si los datos no cambiaron
                sin_cambios = (
                    equipo_existente.edificio == equipo.edificio and
                    equipo_existente.piso == equipo.piso and
                    equipo_existente.version_windows == equipo.version_windows and
                    equipo_existente.nombre_usuario == equipo.nombre_usuario and
                    equipo_existente.usuario == equipo.usuario and
                    equipo_existente.maquina_anterior == equipo.maquina_anterior and
                    equipo_existente.descripcion == equipo.descripcion and
                    equipo_existente.numero_serie == equipo.numero_serie and
                    equipo_existente.fecha_actualizacion == equipo.fecha_actualizacion
                )

                if sin_cambios:
                    log_data = {
                        'maquina': equipo.maquina_actual,
                        'mensaje': 'Equipo ya existe y no hubo cambios'
                    }
                    safe_log('info', 'equipo', log_data, current_user.username)

                    return """
                    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
                    <script>
                        document.addEventListener("DOMContentLoaded", function() {
                            Swal.fire({
                                title: 'Sin cambios',
                                text: 'El equipo ya existe y no se detectaron cambios.',
                                icon: 'info',
                                confirmButtonText: 'Aceptar'
                            }).then(() => {
                                window.opener.location.reload();
                                window.close();
                            });
                        });
                    </script>
                    """

                else:
                    return """
                    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
                    <script>
                        document.addEventListener("DOMContentLoaded", function() {
                            Swal.fire({
                                title: 'Error',
                                text: 'El número de máquina ya existe en otro registro.',
                                icon: 'error',
                                confirmButtonText: 'Aceptar'
                            }).then(() => {
                                window.opener.location.reload();
                                window.close();
                            });
                        });
                    </script>
                    """

            db.session.commit()

            # Registrar edición
            safe_log(
                action='update',
                entity='equipo',
                details={
                    'id': id,
                    'cambios': {
                        'antes': datos_antiguos,
                        'despues': {
                            'edificio': equipo.edificio,
                            'piso': equipo.piso,
                            'maquina_actual': equipo.maquina_actual,
                            'version_windows': equipo.version_windows,
                            'nombre_usuario': equipo.nombre_usuario,
                            'usuario': equipo.usuario,
                            'maquina_anterior': equipo.maquina_anterior,
                            'descripcion': equipo.descripcion,
                            'numero_serie': equipo.numero_serie,
                            'fecha_actualizacion': equipo.fecha_actualizacion
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
                        text: 'Pc actualizada correctamente.',
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
                entity='equipo',
                details={
                    'operation': 'update',
                    'error': str(e),
                    'equipo_id': id
                },
                user=current_user.username
            )
            return "Error al actualizar el equipo", 500
        
    return redirect(url_for('/equipos_aios', id=id))