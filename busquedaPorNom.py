import os

def buscar_archivos(directorio, nombre):
    """
    Busca archivos por nombre en un directorio y sus subdirectorios, sin importar la extensión.

    :param directorio: Ruta del directorio donde se buscará.
    :param nombre: Parte del nombre del archivo a buscar.
    :return: Diccionario con directorios como claves y listas de archivos como valores.
    """
    archivos_por_directorio = {}

    # Recorre el directorio y sus subdirectorios
    for carpeta_actual, _, archivos in os.walk(directorio):
        archivos_encontrados = [
            archivo for archivo in archivos if nombre.lower() in archivo.lower()
        ]

        if archivos_encontrados:
            archivos_por_directorio[carpeta_actual] = archivos_encontrados

    return archivos_por_directorio

# Ejemplo de uso
if __name__ == "__main__":
    # Pedir al usuario los parámetros de búsqueda
    directorio = input("Ingrese la ruta del directorio donde buscar: ").strip()
    nombre = input("Ingrese parte del nombre del archivo a buscar: ").strip()

    # Buscar archivos
    resultados = buscar_archivos(directorio, nombre)

    # Mostrar resultados
    if resultados:
        print(f"\nSe encontraron archivos con el nombre '{nombre}' en los siguientes directorios:")
        for directorio, archivos in resultados.items():
            print(f"\nDirectorio: {directorio}")
            for archivo in archivos:
                print(f"  - {archivo}")
    else:
        print(f"\nNo se encontraron archivos con el nombre '{nombre}'.")
