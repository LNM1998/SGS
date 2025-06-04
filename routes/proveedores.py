from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_required
from models import db, Proveedor

proveedores_bp = Blueprint('proveedores', __name__)

@proveedores_bp.route('/proveedores', methods=['GET'])
@login_required
def proveedores():
    proveedores = Proveedor.query.all()
    return render_template('proveedores.html', proveedores=proveedores)

@proveedores_bp.route('/agregar_proveedor', methods=['GET', 'POST'])
@login_required
def agregar_proveedor():
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        celular = request.form['celular']
        pagina = request.form['pagina']
        observacion = request.form['observacion']
        direccion = request.form['direccion']
        latitud = request.form['latitud']
        longitud = request.form['longitud']
        
        nuevo_proveedor = Proveedor(
            nombre=nombre, 
            telefono=telefono,
            celular=celular,
            pagina=pagina,
            observacion=observacion,
            direccion=direccion,
            latitud=latitud,
            longitud=longitud
        )

        db.session.add(nuevo_proveedor)
        db.session.commit()
        # logger.info(f'{current_user.username} ha agregado un proveedor: {nombre}')
        return """
            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    Swal.fire({
                        title: 'Un Éxito',
                        text: 'Proveedor agregado correctamente.',
                        icon: 'success',
                        confirmButtonText: 'Aceptar'
                    }).then(() => {
                        window.opener.location.reload();
                        window.close();
                    });
                });
            </script>
            """
    
    return render_template('agregar_proveedor.html')

@proveedores_bp.route('/editar_proveedor/<int:id>', methods=['GET'])
@login_required
def editar_proveedor(id):
    proveedor = Proveedor.query.get(id)
    return render_template('/editar_proveedor.html', proveedor=proveedor)

@proveedores_bp.route('/eliminar_proveedor/<int:id>', methods=['POST'])
@login_required
def eliminar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)

    if request.method == 'POST':
        
        db.session.delete(proveedor)
        db.session.commit()
        # logger.info(f'{current_user.username} ha eliminado un proveedor: {proveedor.nombre}')
        return """
            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    Swal.fire({
                        title: 'Un Éxito',
                        text: 'Proveedor eliminado correctamente.',
                        icon: 'success',
                        confirmButtonText: 'Aceptar'
                    }).then(() => {
                        window.opener.location.reload();
                        window.close();
                    });
                });
            </script>
            """
    
    return redirect('/proveedores')

@proveedores_bp.route('/actualizar_proveedor/<int:id>', methods=['POST'])
@login_required
def actualizar_proveedor(id):
    proveedor = Proveedor.query.get(id)

    if request.method == 'POST':
        proveedor.nombre = request.form['nombre']
        proveedor.telefono = request.form['telefono']
        proveedor.celular = request.form['celular']
        proveedor.pagina = request.form['pagina']
        proveedor.observacion = request.form['observacion']
        proveedor.direccion = request.form['direccion']
        proveedor.latitud = request.form['latitud']
        proveedor.longitud = request.form['longitud']
        
        db.session.commit()
        # logger.info(f'{current_user.username} ha editado un proveedor: {proveedor.nombre}')
        return """
            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    Swal.fire({
                        title: 'Un Éxito',
                        text: 'Proveedor editado correctamente.',
                        icon: 'success',
                        confirmButtonText: 'Aceptar'
                    }).then(() => {
                        window.opener.location.reload();
                        window.close();
                    });
                });
            </script>
            """
    
    return redirect(url_for('proveedores', id=id))

