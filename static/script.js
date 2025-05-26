let ordenAscendente = {};

document.addEventListener("DOMContentLoaded", function () {
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

    // const documentList = document.getElementById('document-list');
    // const documentViewer = document.getElementById('document-viewer');

    fetch('/datos')
        .then(response => response.json())
        .then(data => {
            const equipos = data.Equipos;
            const reclamos = data.Reclamos;

            const labels = ["AIOS", "Notebooks", "Impresoras", "Reclamos Bangho", "Reclamos External"];
            const valores = [
                equipos.AIOS,
                equipos.Notebooks,
                equipos.Impresoras,
                reclamos.Bangho,
                reclamos.External
            ];

            const options = {
                series: valores,
                chart: {
                    width: '100%',
                    height: 600,
                    type: 'pie',
                },
                labels: labels,
                colors: ['#003366', '#004080', '#0059b3', '#336699', '#6699cc'], // Tonos de azul oscuro
                plotOptions: {
                    pie: {
                        dataLabels: {
                            offset: -5,
                        },
                    },
                },
                grid: {
                    padding: {
                        top: 0,
                        bottom: 0,
                        left: 0,
                        right: 0,
                    },
                },
                dataLabels: {
                    enabled: true,
                    dropShadow: {
                        enabled: false
                    },
                    style: {
                        fontSize: '14px',
                        fontWeight: 'bold',
                        colors: ['#fff']
                    },
                    formatter: function (val, opts) {
                        const name = opts.w.globals.labels[opts.seriesIndex];
                        const value = opts.w.config.series[opts.seriesIndex];
                        return [name, value]; // 👈 Esto devuelve dos líneas: nombre y valor
                    }
                },                
                legend: {
                    show: true,
                    position: 'bottom', // 👈 Leyenda debajo del gráfico
                    fontSize: '16px',
                    labels: {
                        colors: '#1e3a8a',
                        useSeriesColors: false
                    }
                }                                 
            };            

            const chart = new ApexCharts(document.querySelector("#chart"), options);
            chart.render();
        })
        .catch(error => console.error("Error al cargar los datos:", error));

    fetch('/modificaciones_semanales')
        .then(response => response.json())
        .then(data => {
            // Extraer los valores desde la respuesta del backend
            const valores = [
                data.AIOS,
                data.Notebooks,
                data.ReclamosBangho,
                data.ReclamosExternal
            ];

            const options = {
                series: [{
                    name: 'Modificaciones de la ultima Semana',
                    data: valores
                }],
                chart: {
                    type: 'bar',
                    height: 600
                },
                colors: ['#1e3a8a'], // Azul oscuro
                plotOptions: {
                    bar: {
                        distributed: true,
                        borderRadius: 4,
                        dataLabels: {
                            position: 'top'
                        }
                    }
                },
                dataLabels: {
                    enabled: true,
                    formatter: function (val) {
                        return val.toFixed(0); // Evita NaN
                    },
                    offsetY: -20,
                    style: {
                        fontSize: '14px',
                        colors: ['#1e3a8a']
                    }
                },
                xaxis: {
                    categories: ['AIOS', 'Notebooks', 'Reclamos Bangho', 'Reclamos External'],
                    labels: {
                        style: {
                            fontSize: '14px'
                        }
                    }
                }
            };

            const chart = new ApexCharts(document.querySelector("#graficoBarras"), options);
            chart.render();
        })
        .catch(error => console.error("Error al cargar los datos:", error));

    var filas = document.querySelectorAll(".fila");

    filas.forEach(function(fila) {
        var estado = fila.getAttribute("data-estado").trim().toLowerCase();

        if (estado === "fisica") {fila.classList.add("fila-verde");} 
        else if (estado === "asignada") {fila.classList.add("fila-blanca");} 
        else if (estado === "no devuelta") {fila.classList.add("fila-naranja");}
        else if (estado === "rota") {fila.classList.add("fila-roja");}
        else if (estado === "robada") {fila.classList.add("fila-gris");}
        else if (estado === "perdida") {fila.classList.add("fila-celeste");}
        else if (estado === "baja") {fila.classList.add("fila-naranja");}
        else if (estado === "actualizada") {fila.classList.add("fila-verde");}  
        else if (estado === "pendiente") {fila.classList.add("fila-amarilla");}
    });

    // documentList.addEventListener('click', function (event) {
    //     event.preventDefault();  // Evita que el enlace recargue la página

    //     if (event.target.tagName === 'A') {
    //         const documentName = event.target.getAttribute('data-document');
    //         const documentPath = `{{ url_for('static', filename='documents/') }}${documentName}`;
    //         documentViewer.setAttribute('src', documentPath);
    //     }
    // });

    cambiarFiltro();  // Para que la selección de filtro sea correcta al cargar la página
    actualizarPisosFiltro(); // Para cargar los pisos correctamente si ya hay un edificio seleccionado
});

function cambiarFiltro(sufijo = '') {
    var filtro = document.getElementById("filtro" + sufijo).value;

    // Lista de todos los elementos de filtro
    var filtros = {
        "inputTexto": document.getElementById("valor_input" + sufijo),
        // "selectVersion": document.getElementById("valor_select" + sufijo),
        "selectEdificio": document.getElementById("filtro_edificio" + sufijo),
        "selectPiso": document.getElementById("filtro_piso" + sufijo),
        "selectEstadoNotebook": document.getElementById("filtro_estado_notebook" + sufijo),
        "selectEstadoReclamos": document.getElementById("filtro_estado_reclamos" + sufijo),
        "selectModelo": document.getElementById("filtro_modelo" + sufijo),
        "selectDireccion": document.getElementById("filtro_direccion" + sufijo),
    };

    // Ocultar todos los filtros antes de mostrar el seleccionado
    for (var key in filtros) {
        if (filtros[key]) filtros[key].style.display = "none";
    }

    // Mostrar el filtro correcto según la selección
    switch (filtro) {
        // case "version_windows":
        //     filtros["selectVersion"].style.display = "inline-block";
        //     break;
        case "estado":
            filtros["selectEstadoNotebook"].style.display = "inline-block";
            break;
        case "estado_r":
            filtros["selectEstadoReclamos"].style.display = "inline-block";
            break;
        case "modelo":
            filtros["selectModelo"].style.display = "inline-block";
            break;
        case "direccion":
            filtros["selectDireccion"].style.display = "inline-block";
            break;
        case "edificio":
            filtros["selectEdificio"].style.display = "inline-block";
            filtros["selectPiso"].style.display = "inline-block";
            actualizarPisosFiltro();
            break;
        case "":
            break;
        default:
            filtros["inputTexto"].style.display = "inline-block";
            break;
    }
}

function agregarSegundoFiltro() {
    const contenedor = document.getElementById("segundo-filtro-container");

    // Evitar agregar múltiples veces
    if (document.getElementById("filtro2")) return;

    contenedor.style.display = "block";
    contenedor.innerHTML = `
        <select id="filtro2" name="filtro2" onchange="cambiarFiltro('2')">
            <option value="">Seleccione un filtro</option>
            <option value="edificio">Edificio</option>
            <option value="maquina_actual">Máquina Actual</option>
            <option value="numero_serie">Número de Serie</option>
            <option value="version_windows">Versión de Imagen</option>
            <option value="usuario">Usuario</option>
            <option value="descripcion">Descripción</option>
        </select>

        <!-- Campo texto -->
        <input type="text" id="valor_input2" name="valor2" placeholder="Ingrese el valor" style="display: none;">

        <select id="filtro_edificio2" name="edificio2" style="display: none;" onchange="actualizarPisosFiltro(2)">
            <option value="">Todos los edificios</option>
            <option value="Peru" {% if filtro_edificio2=='Peru' %}selected{% endif %}>Peru</option>
            <option value="Lima" {% if filtro_edificio2=='Lima' %}selected{% endif %}>Lima</option>
            <option value="CAU" {% if filtro_edificio2=='CAU' %}selected{% endif %}>CAU</option>
            <option value="ISER" {% if filtro_edificio2=='ISER' %}selected{% endif %}>ISER</option>
            <option value="CCTE" {% if filtro_edificio2=='CCTE' %}selected{% endif %}>CCTE</option>
            <option value="Museo" {% if filtro_edificio2=='Museo' %}selected{% endif %}>Museo</option>
            <option value="Deposito Mataderos" {% if filtro_edificio2=='Deposito Mataderos' %}selected{% endif %}>Deposito Mataderos</option>
            <option value="Deposito Saldias" {% if filtro_edificio2=='Deposito Saldias' %}selected{% endif %}>Deposito Saldias</option>
        </select>

        <select id="filtro_piso2" name="piso2" style="display: none;">
            <option value="">Seleccione un piso</option>
        </select>
    `;
}

function limpiarFiltros() {
    // Obtener la URL base sin parámetros
    const urlBase = window.location.pathname;

    // Redirigir a la URL base
    window.location.href = urlBase;
}

function abrirVentana(url) {
    let ventana = window.open(url, "_blank", "width=900,height=900");

    // Verificar cada segundo si la ventana fue cerrada
    let checkInterval = setInterval(function() {
        if (ventana.closed) {
            clearInterval(checkInterval);
            location.reload(); // Refresca la página principal después de cerrar la ventana de edición
        }
    }, 1000);
}

function confirmarEliminacion(id) {
    Swal.fire({
        title: '¿Estás seguro?',
        text: "Esta acción no se puede deshacer",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            document.getElementById('eliminarForm' + id).submit();
        }
    });
}

function confirmRoleChange(selectElement) {
    const username = selectElement.dataset.username;
    const newRole = selectElement.value;
    const roleText = selectElement.options[selectElement.selectedIndex].text;
    
    if(confirm(`¿Estás seguro de cambiar el rol de ${username} a ${roleText}?`)) {
        selectElement.form.submit();
    } else {
        // Restaurar valor anterior
        selectElement.value = selectElement.dataset.prevValue;
    }
}

// Guardar valor inicial al cargar
document.querySelectorAll('select[name="new_role"]').forEach(select => {
    select.dataset.prevValue = select.value;
});

function obtenerArticulos() {
    let articulos = [];
    document.querySelectorAll("#tabla-articulos tr").forEach((row, index) => {
        if (index === 0) return;  // Saltar encabezado
        let cantidad = row.querySelector(".articulo-cantidad").value;
        let numero_serie = row.querySelector(".articulo-numero-serie").value;
        let descripcion = row.querySelector(".articulo-descripcion").value;
        let observacion = row.querySelector(".articulo-observacion").value;
        articulos.push({ cantidad, numero_serie, descripcion, observacion });
    });
    document.getElementById("articulos-json").value = JSON.stringify(articulos);
}

function agregarArticulo() {
    let container = document.getElementById("articulos-container");
    let nuevoArticulo = document.createElement("div");
    nuevoArticulo.classList.add("articulo");
    nuevoArticulo.innerHTML = `
        <label>Cantidad:</label>
        <input type="number" name="cantidad[]" placeholder="Cantidad" required>

        <label>Número de Serie:</label>
        <input type="text" name="numero_serie[]" placeholder="Número de Serie" required>

        <label>Descripción:</label>
        <input type="text" name="descripcion[]" placeholder="Descripción" required>

        <label>Observación:</label>
        <input type="text" name="observacion[]" placeholder="Observación">
    `;
    container.appendChild(nuevoArticulo);
}

function validarFormulario() {
    const cantidades = document.querySelectorAll('input[name="cantidad[]"]');
    const numerosSerie = document.querySelectorAll('input[name="numero_serie[]"]');
    const descripciones = document.querySelectorAll('input[name="descripcion[]"]');

    // Verifica que al menos un artículo esté completo
    for (let i = 0; i < cantidades.length; i++) {
        if (!cantidades[i].value || !numerosSerie[i].value || !descripciones[i].value) {
            alert("Todos los campos de los artículos son obligatorios.");
            return false;
        }
    }

    return true;
}

// Función para agregar un nuevo artículo
function agregarArticulo1() {
    const tabla = document.getElementById('tabla-articulos');
    const nuevaFila = document.createElement('tr');

    nuevaFila.innerHTML = `
        <td><input type="number" name="cantidad[]" class="articulo-cantidad" required></td>
        <td><input type="text" name="numero_serie[]" class="articulo-numero-serie" required></td>
        <td><input type="text" name="descripcion[]" class="articulo-descripcion" required></td>
        <td><input type="text" name="observacion_articulo[]" class="articulo-observacion"></td>
        <td><button type="button" onclick="eliminarArticulo(this)">Eliminar</button></td>
    `;

    tabla.appendChild(nuevaFila);
}

// Función para eliminar un artículo
function eliminarArticulo(boton) {
    const fila = boton.closest('tr');
    fila.remove();
}

document.querySelector("form").addEventListener("submit", obtenerArticulos);

$(document).ready(function() {
    $('#tabla-equipos').DataTable({
        "pageLength": 10, // Mostrar 10 registros por página
        "lengthMenu": [[5, 10, 15, 20, 50, -1], [5, 10, 15, 20, 50, "Todos"]], // Opciones de visualización
        "ordering": true, // Permite ordenar columnas
        "searching": false, // Permite buscar
        "language": {
            "lengthMenu": "Mostrar _MENU_",
            "zeroRecords": "No se encontraron registros",
            "info": "Mostrando _START_ a _END_ de _TOTAL_ equipos",
            "infoEmpty": "No hay registros disponibles",
            "infoFiltered": "(filtrado de _MAX_ registros totales)",
            "search": "Buscar:",
            "paginate": {
                "first": "Primero",
                "last": "Último",
                "next": "Siguiente",
                "previous": "Anterior"
            }
        },
        "columnDefs": [
            {
                "targets": 6, // Índice de la columna de fecha (comienza desde 0)
                "type": "date-eu", // Tipo de dato para ordenamiento (reconocerá dd/mm/yyyy)
                "orderSequence": ["desc", "asc"],
                "render": function(data, type, row) {
                    // Mostrar el formato original (dd/mm/yyyy) en la tabla
                    if (type === 'display') {
                        return data === '-' ? '-' : data; 
                    }
                    // Usar yyyy-mm-dd para ordenamiento interno
                    if (type === 'sort') {
                        return data === '-' ? '1900-01-01' : data.split('/').reverse().join('-');
                    }
                    return data;
                }
            }
        ],
    });
    $('#tabla-notebooks').DataTable({
        "pageLength": 10, // Mostrar 10 registros por página
        "lengthMenu": [[5, 10, 15, 20, 50, -1], [5, 10, 15, 20, 50, "Todos"]], // Opciones de visualización
        "ordering": true, // Permite ordenar columnas
        "searching": false, // Permite buscar
        "language": {
            "lengthMenu": "Mostrar _MENU_",
            "zeroRecords": "No se encontraron registros",
            "info": "Mostrando _START_ a _END_ de _TOTAL_ notebooks",
            "infoEmpty": "No hay registros disponibles",
            "infoFiltered": "(filtrado de _MAX_ registros totales)",
            "search": "Buscar:",
            "paginate": {
                "first": "Primero",
                "last": "Último",
                "next": "Siguiente",
                "previous": "Anterior"
            }
        },
        "columnDefs": [
            {
                "targets": 6, // Índice de la columna de fecha (comienza desde 0)
                "type": "date-eu", // Tipo de dato para ordenamiento (reconocerá dd/mm/yyyy)
                "orderSequence": ["desc", "asc"],
                "render": function(data, type, row) {
                    // Mostrar el formato original (dd/mm/yyyy) en la tabla
                    if (type === 'display') {
                        return data === '-' ? '-' : data; 
                    }
                    // Usar yyyy-mm-dd para ordenamiento interno
                    if (type === 'sort') {
                        return data === '-' ? '1900-01-01' : data.split('/').reverse().join('-');
                    }
                    return data;
                }
            }
        ],
    });
    $('#tabla-impresoras').DataTable({
        "pageLength": 10, // Mostrar 10 registros por página
        "lengthMenu": [[5, 10, 15, 20, 50, -1], [5, 10, 15, 20, 50, "Todos"]], // Opciones de visualización
        "ordering": true, // Permite ordenar columnas
        "searching": false, // Permite buscar
        "language": {
            "lengthMenu": "Mostrar _MENU_",
            "zeroRecords": "No se encontraron registros",
            "info": "Mostrando _START_ a _END_ de _TOTAL_ impresoras",
            "infoEmpty": "No hay registros disponibles",
            "infoFiltered": "(filtrado de _MAX_ registros totales)",
            "search": "Buscar:",
            "paginate": {
                "first": "Primero",
                "last": "Último",
                "next": "Siguiente",
                "previous": "Anterior"
            }
        }
    });
    $('#tabla-hardware').DataTable({
        "pageLength": 10, // Mostrar 10 registros por página
        "lengthMenu": [[5, 10, 15, 20, 50, -1], [5, 10, 15, 20, 50, "Todos"]], // Opciones de visualización
        "ordering": true, // Permite ordenar columnas
        "searching": false, // Permite buscar
        "language": {
            "lengthMenu": "Mostrar _MENU_",
            "zeroRecords": "No se encontraron registros",
            "info": "Mostrando _START_ a _END_ de _TOTAL_ impresoras",
            "infoEmpty": "No hay registros disponibles",
            "infoFiltered": "(filtrado de _MAX_ registros totales)",
            "search": "Buscar:",
            "paginate": {
                "first": "Primero",
                "last": "Último",
                "next": "Siguiente",
                "previous": "Anterior"
            }
        }
    });
    $('#tabla-reclamos-b').DataTable({
        "pageLength": 10, // Mostrar 10 registros por página
        "lengthMenu": [[5, 10, 15, 20, 50, -1], [5, 10, 15, 20, 50, "Todos"]], // Opciones de visualización
        "order": [[2, "desc"]],  // Ordenar por la columna 2 (N° Referencia) en orden descendente
        "searching": false, // Permite buscar
        "language": {
            "lengthMenu": "Mostrar _MENU_",
            "zeroRecords": "No se encontraron registros",
            "info": "Mostrando _START_ a _END_ de _TOTAL_ reclamos",
            "infoEmpty": "No hay registros disponibles",
            "infoFiltered": "(filtrado de _MAX_ registros totales)",
            "search": "Buscar:",
            "paginate": {
                "first": "Primero",
                "last": "Último",
                "next": "Siguiente",
                "previous": "Anterior"
            }
        },
        "columnDefs": [
            {
                "targets": 4, // Índice de la columna de fecha (comienza desde 0)
                "type": "date-eu", // Tipo de dato para ordenamiento (reconocerá dd/mm/yyyy)
                "orderSequence": ["desc", "asc"],
                "render": function(data, type, row) {
                    // Mostrar el formato original (dd/mm/yyyy) en la tabla
                    if (type === 'display') {
                        return data === '-' ? '-' : data; 
                    }
                    // Usar yyyy-mm-dd para ordenamiento interno
                    if (type === 'sort') {
                        return data === '-' ? '1900-01-01' : data.split('/').reverse().join('-');
                    }
                    return data;
                }
            }
        ],
    });
    $('#tabla-reclamos-e').DataTable({
        "pageLength": 10, // Mostrar 10 registros por página
        "lengthMenu": [[5, 10, 15, 20, 50, -1], [5, 10, 15, 20, 50, "Todos"]], // Opciones de visualización
        "order": [[4, "desc"]],
        "searching": false, // Permite buscar
        "language": {
            "lengthMenu": "Mostrar _MENU_",
            "zeroRecords": "No se encontraron registros",
            "info": "Mostrando _START_ a _END_ de _TOTAL_ reclamos",
            "infoEmpty": "No hay registros disponibles",
            "infoFiltered": "(filtrado de _MAX_ registros totales)",
            "search": "Buscar:",
            "paginate": {
                "first": "Primero",
                "last": "Último",
                "next": "Siguiente",
                "previous": "Anterior"
            }
        },
        "columnDefs": [
            {
                "targets": 4, // Índice de la columna de fecha (comienza desde 0)
                "type": "date-eu", // Tipo de dato para ordenamiento (reconocerá dd/mm/yyyy)
                "orderSequence": ["desc", "asc"],
                "render": function(data, type, row) {
                    // Mostrar el formato original (dd/mm/yyyy) en la tabla
                    if (type === 'display') {
                        return data === '-' ? '-' : data; 
                    }
                    // Usar yyyy-mm-dd para ordenamiento interno
                    if (type === 'sort') {
                        return data === '-' ? '1900-01-01' : data.split('/').reverse().join('-');
                    }
                    return data;
                }
            }
        ],
    });
    $('#tabla-gestion-usuarios').DataTable({
        "pageLength": 10, // Mostrar 10 registros por página
        "lengthMenu": [[5, 10, 15, 20, 50, -1], [5, 10, 15, 20, 50, "Todos"]], // Opciones de visualización
        "ordering": true, // Permite ordenar columnas
        "searching": true, // Permite buscar
        "language": {
            "lengthMenu": "Mostrar _MENU_",
            "zeroRecords": "No se encontraron registros",
            "info": "Mostrando _START_ a _END_ de _TOTAL_ usuarios",
            "infoEmpty": "No hay registros disponibles",
            "infoFiltered": "(filtrado de _MAX_ registros totales)",
            "search": "Buscar:",
            "paginate": {
                "first": "Primero",
                "last": "Último",
                "next": "Siguiente",
                "previous": "Anterior"
            }
        }
    });
    $('#tabla-remitos').DataTable({
        "pageLength": 10, // Mostrar 10 registros por página
        "lengthMenu": [[5, 10, 15, 20, 50, -1], [5, 10, 15, 20, 50, "Todos"]], // Opciones de visualización
        "order": [[4, "desc"]],
        "searching": true, // Permite buscar
        "language": {
            "lengthMenu": "Mostrar _MENU_",
            "zeroRecords": "No se encontraron registros",
            "info": "Mostrando _START_ a _END_ de _TOTAL_ remitos",
            "infoEmpty": "No hay registros disponibles",
            "infoFiltered": "(filtrado de _MAX_ registros totales)",
            "search": "Buscar:",
            "paginate": {
                "first": "Primero",
                "last": "Último",
                "next": "Siguiente",
                "previous": "Anterior"
            }
        },
        "columnDefs": [
            {
                "targets": 2, // Índice de la columna de fecha (comienza desde 0)
                "type": "date-eu", // Tipo de dato para ordenamiento (reconocerá dd/mm/yyyy)
                "orderSequence": ["desc", "asc"],
                "render": function(data, type, row) {
                    // Mostrar el formato original (dd/mm/yyyy) en la tabla
                    if (type === 'display') {
                        return data === '-' ? '-' : data; 
                    }
                    // Usar yyyy-mm-dd para ordenamiento interno
                    if (type === 'sort') {
                        return data === '-' ? '1900-01-01' : data.split('/').reverse().join('-');
                    }
                    return data;
                }
            }
        ],
    });
    $('#tabla-articulos').DataTable({
        "pageLength": 10, // Mostrar 10 registros por página
        "lengthMenu": [[5, 10, 15, 20, 50, -1], [5, 10, 15, 20, 50, "Todos"]], // Opciones de visualización
        "ordering": true, // Permite ordenar columnas
        "searching": true, // Permite buscar
        "language": {
            "lengthMenu": "Mostrar _MENU_",
            "zeroRecords": "No se encontraron registros",
            "info": "Mostrando _START_ a _END_ de _TOTAL_ usuarios",
            "infoEmpty": "No hay registros disponibles",
            "infoFiltered": "(filtrado de _MAX_ registros totales)",
            "search": "Buscar:",
            "paginate": {
                "first": "Primero",
                "last": "Último",
                "next": "Siguiente",
                "previous": "Anterior"
            }
        }
    });
});

$(document).ready(function() {
    var table = $('#miTabla').DataTable();

    // Mover el control de paginación al contenedor de filtros
    $('.dataTables_length').appendTo('.filtros-container');
    $('.dataTables_filter').appendTo('.filtros-container');
});


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
    } else if (edificio === "Lima") {
        for (let i = 0; i <= 13; i++) {
            pisos.push(i);
        }
    } else if (edificio === "CAU") {
        for (let i = 0; i <= 2; i++) {
            pisos.push(i);
        }
    } else if (edificio === "ISER") {
        for (let i = 0; i <= 4; i++) {
            pisos.push(i);
        }
    } else if (edificio === "CCTE") {
        pisos.push("CCTE-BS. AS.");
        pisos.push("CCTE-COMODORO");
        pisos.push("CCTE-CORDOBA");
        pisos.push("CCTE-NEUQUEN");
        pisos.push("CCTE-POSADAS");
        pisos.push("CCTE-SALTA");
    } else if (edificio === "Museo") {
        pisos.push("Museo");
    } else if (edificio === "Deposito Mataderos") {
        pisos.push("Deposito Mataderos");
    } else if (edificio === "Deposito Saldias") {
        pisos.push("Deposito Saldias");
    }

    // Agregar nuevas opciones
    pisos.forEach(piso => {
        let option = document.createElement("option");
        option.value = piso;
        option.textContent = piso;
        pisoSelect.appendChild(option);
    });
}

function actualizarPisosFiltro(origen = 1) {
    let edificio = document.getElementById(origen === 2 ? "filtro_edificio2" : "filtro_edificio").value;
    let pisoSelect = document.getElementById(origen === 2 ? "filtro_piso2" : "filtro_piso");

    // Guardar el edificio seleccionado en sessionStorage
    // sessionStorage.setItem("edificioSeleccionado", edificio);

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
    } else if (edificio === "Lima") {
        for (let i = 0; i <= 13; i++) {
            pisos.push(i);
        }
    } else if (edificio === "ISER") {
        for (let i = 0; i <= 4; i++) {
            pisos.push(i);
        }
    } else if (edificio === "CCTE") {
        pisos.push("CCTE-BS. AS.");
        pisos.push("CCTE-COMODORO");
        pisos.push("CCTE-CORDOBA");
        pisos.push("CCTE-NEUQUEN");
        pisos.push("CCTE-POSADAS");
        pisos.push("CCTE-SALTA");
    } else if (edificio === "Museo") {
        pisos.push("Museo");
    } else if (edificio === "Deposito Mataderos") {
        pisos.push("Deposito Mataderos");
    } else if (edificio === "Deposito Saldias") {
        pisos.push("Deposito Saldias");
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
// actualizarPisosFiltro();

// Guardar la selección del piso cuando cambia
pisoSelect.addEventListener("change", function () {
    sessionStorage.setItem("pisoSeleccionado", pisoSelect.value);
});
