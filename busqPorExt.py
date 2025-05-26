import os

def buscar_archivos(directorio, extension):
    """
    Busca archivos por nombre y extensión en un directorio y sus subdirectorios.

    :param directorio: Ruta del directorio donde se buscará.
    :param nombre: Parte del nombre del archivo a buscar.
    :param extension: Extensión de los archivos a buscar (por ejemplo, ".pst").
    :return: Diccionario con directorios como claves y listas de archivos como valores.
    """
    archivos_por_directorio = {}

    # Recorre el directorio y sus subdirectorios
    for carpeta_actual, _, archivos in os.walk(directorio):
        archivos_encontrados = [
            archivo for archivo in archivos
            if archivo.endswith(extension)
        ]

        if archivos_encontrados:
            archivos_por_directorio[carpeta_actual] = archivos_encontrados

    return archivos_por_directorio

# Ejemplo de uso
if __name__ == "__main__":
    # Pedir al usuario los parámetros de búsqueda
    directorio = input("Ingrese la ruta del directorio donde buscar: ").strip()
    extension = input("Ingrese la extensión del archivo (ejemplo: .pst): ").strip()

    # Validar que la extensión comience con un punto
    if not extension.startswith("."):
        extension = "." + extension

    # Buscar archivos
    resultados = buscar_archivos(directorio, extension)

    # Mostrar resultados
    if resultados:
        print(f"\nSe encontraron archivos con la extensión '{extension}' en los siguientes directorios:")
        for directorio, archivos in resultados.items():
            print(f"\nDirectorio: {directorio}")
            for archivo in archivos:
                print(f"  - {archivo}")
    else:
        print(f"\nNo se encontraron archivos con la extensión '{extension}'.")
