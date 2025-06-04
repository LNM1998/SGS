from pathlib import Path
from datetime import datetime
import os
from flask import current_app

class FileLogger:
    def __init__(self):
        self._is_initialized = False  # Atributo interno privado
        self.logs_dir = None
        self.log_file = None
        self.app = None
    
    def init_app(self, app):
        """Inicialización segura del logger"""
        self.app = app
        
        try:
            # Configuración de rutas
            self.logs_dir = Path(app.root_path) / 'static' / 'logs'
            self.log_file = self.logs_dir / 'system_operations.log'
            
            # Crear directorio si no existe
            self.logs_dir.mkdir(parents=True, exist_ok=True)
            
            # Verificación de escritura
            # test_msg = f"Prueba de inicialización - {datetime.now()}\n"
            # with open(self.log_file, 'a', encoding='utf-8') as f:
            #     f.write(test_msg)
            #     f.flush()
            #     os.fsync(f.fileno())
            
            app.logger.info(f"Logger configurado en {self.log_file}")
            self._is_initialized = True
            
        except Exception as e:
            app.logger.error(f"Error inicializando logger: {str(e)}")
            raise RuntimeError(f"No se pudo inicializar el logger: {str(e)}")

    @property
    def is_initialized(self):
        """Propiedad pública para verificar estado"""
        return self._is_initialized

    def log(self, action, entity, details, user=None):
        """Método seguro para registrar logs"""
        if not self._is_initialized:
            if self.app:
                self.app.logger.error("Logger usado sin inicializar!")
            raise RuntimeError("Logger no inicializado. Llama a init_app() primero")
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            user = user or 'anonymous'
            details_str = str(details) if not isinstance(details, str) else details
            log_entry = f"[{timestamp}] [{action.upper()}] [{entity}] [{user}] {details_str}\n"
            
            # Escritura garantizada
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                f.flush()
                os.fsync(f.fileno())
            
            # Registrar también en el logger de Flask si está disponible
            if self.app:
                self.app.logger.info(f"Log registrado: {action}/{entity}")
                
        except Exception as e:
            if self.app:
                self.app.logger.error(f"Error escribiendo log: {str(e)}")
            raise

# Instancia única del logger
logger = FileLogger()