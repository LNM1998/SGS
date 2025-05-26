from flask import Blueprint, request, render_template, redirect, url_for, current_app
from flask_login import login_required, current_user
from pathlib import Path
from models import db, Hardware
from .auth import lectura_allowed, basico_required
from .logs import logger

hardware_bp = Blueprint('hardware', __name__)

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


@hardware_bp.route('/hardware', methods=['GET'])
@login_required
@lectura_allowed
def hardware():
    filtro = request.args.get('filtro', '')
    valor = request.args.get('valor', '')
    filtro_edificio = request.args.get('edificio', '')
    filtro_piso = request.args.get('piso', '')

    # Construimos la consulta base
    consulta = Hardware.query

    # Filtrar por edificio
    if filtro_edificio:
        consulta = consulta.filter(Hardware.edificio == filtro_edificio)
        if filtro_piso:  # Si también se selecciona un piso
            consulta = consulta.filter(Hardware.piso == filtro_piso)

    if filtro and valor:
        if filtro == 'nombre':
            consulta = consulta.filter(Hardware.nombre.contains(valor))
        elif filtro == 'numero_serie':
            consulta = consulta.filter(Hardware.numero_serie.contains(valor))
        elif filtro == 'inventario':
            consulta = consulta.filter(Hardware.inventario.contains(valor))
        elif filtro == 'descripcion':
            consulta = consulta.filter(Hardware.descripcion.contains(valor))

    hardware = consulta.all()
    return render_template('hardware.html', hardware=hardware, filtro=filtro, valor=valor, filtro_edificio=filtro_edificio, filtro_piso=filtro_piso)

@hardware_bp.route('/agregar_hardware', methods=['GET', 'POST'])
@login_required
@basico_required
def agregar_hardware():
    if request.method == 'POST':
        try:
            # Recoger datos del formulario
            form_data = {
                'edificio': request.form.get('edificio', '').strip(),
                'piso': request.form.get('piso', '').strip(),
                'nombre': request.form.get('nombre', '').strip(),
                'inventario': request.form.get('inventario', '').strip(),
                'numero_serie': request.form.get('numero_serie', '').strip(),
                'usuario': request.form.get('usuario', '').strip(),
                'descripcion': request.form.get('descripcion', '').strip(),
            }

            # Verificar si el equipo ya existe
            hardware_existente = Hardware.query.filter_by(inventario=form_data['inventario']).first()
            if hardware_existente:
                log_data = {
                    'inventario': form_data['inventario'],
                    'intento': form_data,
                    'mensaje': 'Equipo ya existe en la base de datos'
                }
                safe_log('conflict', 'hardware', log_data, current_user.username)
                return """
                <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
                <script>
                    document.addEventListener("DOMContentLoaded", function() {
                        Swal.fire({
                            title: 'Error',
                            text: 'El número de inventario ya existe.',
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
            nuevo_hardware = Hardware(
                edificio=form_data['edificio'],
                piso=form_data['piso'],
                nombre=form_data['nombre'],
                inventario=form_data['inventario'] or None,
                numero_serie=form_data['numero_serie'] or None,
                usuario=form_data['usuario'] or None,
                descripcion=form_data['descripcion'],
            )

            db.session.add(nuevo_hardware)
            db.session.commit()

            safe_log(
                action='create',
                entity='hardware',
                details={
                    'id': nuevo_hardware.id,
                    'edificio': nuevo_hardware.edificio,
                    'piso': nuevo_hardware.piso,
                    'nombre': nuevo_hardware.nombre,
                    'inventario': nuevo_hardware.inventario,
                    'numero_serie': nuevo_hardware.numero_serie,
                    'usuario': nuevo_hardware.usuario,
                    'descripcion': nuevo_hardware.descripcion,
                },
                user=current_user.username
            )

            return """
            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    Swal.fire({
                        title: 'Un Éxito',
                        text: 'Hardware agregado correctamente.',
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
            
            current_app.logger.error(f"Error en agregar_hardware: {str(e)}")
            safe_log(
                action='error',
                entity='hardware',
                details={'error': str(e), 'operacion': 'agregar_hardware'},
                user=current_user.username
            )

            return """
            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    Swal.fire({
                        title: 'Error',
                        text: 'Ocurrió un error al agregar el nuevo hardware.',
                        icon: 'error',
                        confirmButtonText: 'Aceptar'
                    }).then(() => {
                        window.opener.location.reload();
                        window.close();
                    });
                });
            </script>
            """

    return render_template('agregar_hardware.html')

@hardware_bp.route('/eliminar_hardware/<int:id>', methods=['POST'])
@login_required
@basico_required
def eliminar_hardware(id):
    try:
        hardware = Hardware.query.get_or_404(id)
        
        # Registrar datos antes de eliminar
        safe_log(
            action='delete',
            entity='hardware',
            details={
                'id': id,
                'edificio': hardware.edificio,
                'piso': hardware.piso,
                'nombre': hardware.nombre,
                'inventario': hardware.inventario,
                'numero_serie': hardware.numero_serie,
                'usuario': hardware.usuario,
                'descripcion': hardware.descripcion,
            },
            user=current_user.username
        )

        db.session.delete(hardware)
        db.session.commit()

        return redirect('/hardware')
    
    except Exception as e:
        db.session.rollback()
        safe_log(
            action='error',
            entity='hardware',
            details={
                'operation': 'delete',
                'error': str(e),
                'hardware_id': id
            },
            user=current_user.username
        )
        return "Error al eliminar el equipo", 500

@hardware_bp.route('/editar_hardware/<int:id>', methods=['GET'])
@login_required
@basico_required
def editar_hardware(id):
    hardware = Hardware.query.get(id)

    return render_template('editar_hardware.html', hardware=hardware)

@hardware_bp.route('/actualizar_hardware/<int:id>', methods=['POST'])
@login_required
@basico_required
def actualizar_hardware(id):
    hardware = Hardware.query.get(id)

    if request.method == 'POST':
        try:
            # Capturar datos antiguos para el log
            datos_antiguos = {
                'edificio': hardware.edificio,
                'piso': hardware.piso,
                'nombre': hardware.nombre,
                'inventario': hardware.inventario,
                'numero_serie': hardware.numero_serie,
                'usuario': hardware.usuario,
                'descripcion': hardware.descripcion,
            }

            hardware.edificio = request.form['edificio']
            hardware.piso = request.form['piso']
            hardware.nombre = request.form['nombre']
            hardware.inventario = request.form['inventario'] or None
            hardware.numero_serie = request.form['numero_serie'] or None
            hardware.usuario = request.form['usuario'] or None
            hardware.descripcion = request.form['descripcion']

            db.session.commit()

            # Registrar edición
            safe_log(
                action='update',
                entity='hardware',
                details={
                    'id': id,
                    'cambios': {
                        'antes': datos_antiguos,
                        'despues': {
                            'edificio': hardware.edificio,
                            'piso': hardware.piso,
                            'nombre': hardware.nombre,
                            'inventario': hardware.inventario,
                            'numero_serie': hardware.numero_serie,
                            'usuario': hardware.usuario,
                            'descripcion': hardware.descripcion,
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
                        text: 'Hardware actualizado correctamente.',
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
                entity='hardware',
                details={
                    'operation': 'update',
                    'error': str(e),
                    'hardware_id': id
                },
                user=current_user.username
            )
            return "Error al actualizar hardware", 500
        
    return redirect(url_for('/hardware', id=id))