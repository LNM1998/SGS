from flask import render_template, request, redirect, url_for, send_from_directory, Response, Blueprint, jsonify
from flask_login import login_required
import os

documentacion_bp = Blueprint('documentacion', __name__)

# Configuración para la subida de archivos
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads/documentacion')
ALLOWED_EXTENSIONS = {'pdf'}

# Crear la carpeta de uploads si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Función para verificar la extensión del archivo
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta principal para mostrar la documentación
@documentacion_bp.route('/documentacion')
@login_required
def documentacion():
    # Leer los archivos PDF subidos
    files = os.listdir(UPLOAD_FOLDER)
    files = [file for file in files if file.endswith('.pdf')]  # Solo mostrar PDFs
    return render_template('documentacion.html', files=files)

# Ruta para subir archivos
@documentacion_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No se ha seleccionado ningún archivo.'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No se ha seleccionado ningún archivo.'}), 400
    
    # Verificar si el archivo es un PDF
    if file and allowed_file(file.filename):
        # Limpiar el nombre del archivo (opcional)
        filename = file.filename  # O usar una función personalizada para limpiar el nombre
        
        # Guardar el archivo en la carpeta de subidas
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        
        return jsonify({'success': True, 'message': 'Archivo subido correctamente.'}), 200
    else:
        return jsonify({'success': False, 'message': 'Solo se permiten archivos PDF.'}), 400
    #     return redirect(url_for('documentacion.documentacion'))

    # return redirect(request.url)

# Ruta para eliminar un archivo PDF
@documentacion_bp.route('/documentacion/delete/<filename>', methods=['DELETE'])
@login_required
def delete_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        return '', 204  # Respuesta sin contenido (eliminación exitosa)
    else:
        return "Archivo no encontrado", 404


# Ruta para servir archivos PDF con soporte para solicitudes de rango
@documentacion_bp.route('/uploads/documentacion/<filename>')
@login_required
def uploaded_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Verificar si el archivo existe
    if not os.path.exists(file_path):
        return "Archivo no encontrado", 404
    
    # Manejar solicitudes de rango
    range_header = request.headers.get('Range')
    if not range_header:
        return send_from_directory(UPLOAD_FOLDER, filename)
    
    file_size = os.path.getsize(file_path)
    start, end = range_header.replace('bytes=', '').split('-')
    start = int(start)
    end = int(end) if end else file_size - 1
    
    with open(file_path, 'rb') as f:
        f.seek(start)
        chunk = f.read(end - start + 1)
    
    response = Response(chunk, 206, mimetype='application/pdf', direct_passthrough=True)
    response.headers.add('Content-Range', f'bytes {start}-{end}/{file_size}')
    response.headers.add('Accept-Ranges', 'bytes')
    response.headers.add('Content-Length', str(end - start + 1))
    
    return response


