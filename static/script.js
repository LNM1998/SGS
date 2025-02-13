let ordenAscendente = {};

document.addEventListener("DOMContentLoaded", function () {
    cambiarFiltro();  // Para que la selección de filtro sea correcta al cargar la página
    actualizarPisos(); // Para cargar los pisos correctamente si ya hay un edificio seleccionado

    // Obtener referencias a los selects
    let edificioSelect = document.getElementById("filtro_edificio");
    let pisoSelect = document.getElementById("filtro_piso");

    // Recuperar selección anterior de sessionStorage
    let edificioSeleccionado = sessionStorage.getItem("edificioSeleccionado") || "";
    let pisoSeleccionado = sessionStorage.getItem("pisoSeleccionado") || "";

    // Restaurar selección del edificio si había una guardada
    if (edificioSeleccionado) {
        edificioSelect.value = edificioSeleccionado;
    }

    window.ordenarTabla = function (columna) {
        let tabla = document.getElementById("tabla-equipos");
        let filas = Array.from(tabla.rows).slice(1); // Obtener todas las filas excepto el encabezado

        // Alternar orden de la columna seleccionada
        ordenAscendente[columna] = !ordenAscendente[columna];

        // Detectar si la columna contiene números o texto
        let esNumerico = filas.every(fila => !isNaN(fila.cells[columna].innerText.trim()));

        filas.sort((a, b) => {
            let valorA = a.cells[columna].innerText.trim();
            let valorB = b.cells[columna].innerText.trim();

            if (esNumerico) {
                return ordenAscendente[columna] ? valorA - valorB : valorB - valorA;
            } else {
                return ordenAscendente[columna] ? valorA.localeCompare(valorB) : valorB.localeCompare(valorA);
            }
        });

        // Limpiar y reinsertar filas ordenadas
        filas.forEach(fila => tabla.appendChild(fila));

        // Actualizar iconos de flecha
        let iconos = document.querySelectorAll("th i");
        iconos.forEach(icono => icono.className = "fas fa-sort");

        let icono = tabla.rows[0].cells[columna].querySelector("i");
        icono.className = ordenAscendente[columna] ? "fas fa-sort-up" : "fas fa-sort-down";
    };
});

function cambiarFiltro() {
    var filtro = document.getElementById("filtro").value;
    var inputTexto = document.getElementById("valor_input");
    var selectVersion = document.getElementById("valor_select");
    var selectEdificio = document.getElementById("filtro_edificio");
    var selectPiso = document.getElementById("filtro_piso");

    // Mostrar/ocultar elementos según el filtro seleccionado
    if (filtro === "version_windows") {
        inputTexto.style.display = "none";
        selectVersion.style.display = "inline-block";
        selectEdificio.style.display = "none";
        selectPiso.style.display = "none";
    } else if (filtro === "edificio") {
        inputTexto.style.display = "none";
        selectVersion.style.display = "none";
        selectEdificio.style.display = "inline-block";
        selectPiso.style.display = "inline-block"; // Mostrar pisos según edificio seleccionado
        actualizarPisos(); // Llamar función para actualizar pisos
    } else {
        inputTexto.style.display = "inline-block";
        selectVersion.style.display = "none";
        selectEdificio.style.display = "none";
        selectPiso.style.display = "none";
    }
}

function limpiarFiltros() {
    // Redirigir a la página sin parámetros de búsqueda
    window.location.href = "/";
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

    // Agregar nuevas opciones
    pisos.forEach(piso => {
        let option = document.createElement("option");
        option.value = piso;
        option.textContent = piso;
        pisoSelect.appendChild(option);
    });
}

function actualizarPisosFiltro() {
    let edificio = document.getElementById("filtro_edificio").value;
    let pisoSelect = document.getElementById("filtro_piso");

    // Guardar el edificio seleccionado en sessionStorage
    sessionStorage.setItem("edificioSeleccionado", edificio);

    // Limpiar opciones anteriores y ocultar si no hay edificio
    pisoSelect.innerHTML = '<option value="">Seleccione un piso</option>';
    if (!edificio) {
        pisoSelect.style.display = "none";
        sessionStorage.removeItem("pisoSeleccionado"); // Limpiar almacenamiento
        return;
    } else {
        pisoSelect.style.display = "inline-block";
    }

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

    // Agregar nuevas opciones al select
    pisos.forEach(piso => {
        let option = document.createElement("option");
        option.value = piso;
        option.textContent = piso;
        pisoSelect.appendChild(option);
    });

    // Restaurar selección de piso si sigue siendo válido
    if (pisoSeleccionado && pisos.includes(parseInt(pisoSeleccionado))) {
        pisoSelect.value = pisoSeleccionado;
    }
}

// Ejecutar la función al cargar la página para restaurar selección
actualizarPisosFiltro();

// Guardar la selección del piso cuando cambia
pisoSelect.addEventListener("change", function () {
    sessionStorage.setItem("pisoSeleccionado", pisoSelect.value);
});




