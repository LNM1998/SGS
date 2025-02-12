function cambiarFiltro() {
    var filtro = document.getElementById("filtro").value;
    var inputTexto = document.getElementById("valor_input");
    var selectVersion = document.getElementById("valor_select");

    if (filtro === "version_windows") {
        inputTexto.style.display = "none"; // Ocultar input de texto
        selectVersion.style.display = "inline-block"; // Mostrar lista desplegable
    } else {
        inputTexto.style.display = "inline-block"; // Mostrar input de texto
        selectVersion.style.display = "none"; // Ocultar lista desplegable
    }
}

function actualizarPisos() {
    let edificio = document.getElementById("edificio").value;
    let pisoSelect = document.getElementById("piso");

    // Limpiar opciones anteriores
    pisoSelect.innerHTML = '<option value="">Seleccione un piso</option>';

    let pisos = [];

    if (edificio === "Peru") {
        for (let i = -3; i <= 20; i++) {
            pisos.push(i);
        }
    } else if (edificio === "CAU") {
        for (let i = 0; i <= 2; i++) {
            pisos.push(i);
        }
    }

    // Agregar nuevas opciones si hay pisos disponibles
    if (pisos.length > 0) {
        pisos.forEach(piso => {
            let option = document.createElement("option");
            option.value = piso;
            option.textContent = piso;
            pisoSelect.appendChild(option);
        });
    }
}
// Llamar a la función al cargar la página para mantener la selección correcta
document.addEventListener("DOMContentLoaded", cambiarFiltro);
