// Espera a que el DOM esté completamente cargado
let numeroDeArticulos = 0;
document.addEventListener('DOMContentLoaded', function() {
    // Obtener el ID de la empresa desde una variable global de Django o desde el contexto
    const idEmpresa = "{{ id_empresa }}"; // Asegúrate de pasar esta variable desde tu vista de Django

    // Función para actualizar la cantidad del carrito
    function actualizarCantidadCarrito() {
        fetch(`cantidad/`)
            .then(response => response.json())
            .then(data => {
                const badgeCarrito = document.getElementById('badgeCarrito');
                badgeCarrito.textContent = data.cantidad_carrito;
            })
            .catch(error => console.error('Error al obtener la cantidad del carrito:', error));
    }

    // Llama a la función para actualizar la cantidad cuando se carga la página
    actualizarCantidadCarrito();

    window.addEventListener('pageshow', function(event) {
        if (event.persisted) {  // Detecta si la página se muestra desde la caché del navegador
            actualizarCantidadCarrito();
        }
    });

});

document.addEventListener('DOMContentLoaded', function() {
    // Selecciona todos los tbodys que necesiten gestionar los clics
    const tbodys = document.querySelectorAll('tbody[id^="articulosList"]'); // Por ejemplo, todos los IDs que empiezan con "carrito-"

    tbodys.forEach(tbody => {
        tbody.addEventListener('click', function(event) {
            if (event.target.closest('.agregar-carrito')) {
                const boton = event.target.closest('.agregar-carrito'); // Obtén el botón
                const articuloId = boton.getAttribute('data-id'); // Obtén el ID del artículo
                // Realiza la solicitud Fetch para agregar al carrito
                const fila = boton.closest('tr');

                // Obtener la cantidad de la columna de la tabla
                const cantidadInput = fila.querySelector('.cantidad-plus'); // Asumiendo que la clase de la columna de cantidad es "cantidad"
                const valor = cantidadInput.value.replace(',', '.');
                const cantidad = (valor && !isNaN(valor) && valor !== '') ? parseFloat(valor) : 1;
                console.log(cantidad)
                // Crear un objeto con los datos a enviar
                const data = {
                    cantidad: cantidad
                };

                fetch(`agregar/${articuloId}/`, {
                    method: 'POST',  // Cambiamos a POST para enviar datos
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken') // Asegúrate de enviar el CSRF token para solicitudes POST
                    },
                    body: JSON.stringify(data) // Convertir el objeto de datos a JSON
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            numeroDeArticulos = data.cantidad_total; // Actualiza el número de artículos
                            actualizarBadgeCarrito();
                            cantidadInput.value = ''
                        } else {
                            alert('Stock Insuficiente')
                        }
                    })
                    .catch(error => console.error('Error al agregar al carrito:', error));
            }
        });
    });
});
function actualizarBadgeCarrito() {
    const badgeCarrito = document.getElementById('badgeCarrito');
    badgeCarrito.textContent = numeroDeArticulos; // Actualiza el texto del badge
}
document.addEventListener("click", function(e) {
    const target = e.target;
    // Verifica si el clic fue en el botón o en un hijo del botón
    if (target.classList.contains("actualizar-stock") || target.closest(".actualizar-stock")) {
        const boton = target.closest(".actualizar-stock"); // Obtén el botón
        const idArticulo = boton.getAttribute("data-id-articulo");
        const descripcion = document.getElementById(`descri${idArticulo}`);
        const cantidad = document.getElementById('cantidadMovimientor')
        cantidad.value = ''
        // Lógica para abrir el modal
        const idart_modal = document.getElementById('idartr')
        idart_modal.innerText = idArticulo
        const descriart_modal = document.getElementById('descriartr')
        descriart_modal.innerHTML = descripcion.textContent;
        $("#regularizaStockModal").modal("show");
    }
});

document.addEventListener("click", function(e) {
    const target = e.target;
    // Verifica si el clic fue en el botón o en un hijo del botón
    if (target.classList.contains("entrada-stock") || target.closest(".entrada-stock")) {
        const boton = target.closest(".entrada-stock"); // Obtén el botón
        const idArticulo = boton.getAttribute("data-id-articulo");
        const descripcion = document.getElementById(`descri${idArticulo}`);
        // Lógica para abrir el modal
        const idart_modal = document.getElementById('idarte')
        idart_modal.innerText = idArticulo
        const descriart_modal = document.getElementById('descriarte')
        descriart_modal.innerHTML = descripcion.textContent;    
        const cantidad = document.getElementById('cantidadMovimientoe')
        cantidad.value = ''
        const documentoe = document.getElementById('documentoe')
        documentoe.value = ''

        const fila = boton.closest("tr"); 
    
    // Encuentra la celda de precio de compra en la misma fila
        const precioCompraCelda = fila.querySelector(".preciocompra");
        
        // Recupera el valor del precio de compra de la celda
        const precio_compra = precioCompraCelda.textContent; 

        const precio_compra_num = precio_compra.replace(/\./g, '').replace(',', '.');
        const precio_compra_modal = document.getElementById('precioComprae');
        precio_compra_modal.value = parseFloat(precio_compra_num);
        $("#entradaStockModal").modal("show");
    }
});

document.addEventListener("click", function(e) {
    const target = e.target;
    // Verifica si el clic fue en el botón o en un hijo del botón
    if (target.classList.contains("salida-stock") || target.closest(".salida-stock")) {
        const boton = target.closest(".salida-stock"); // Obtén el botón
        const idArticulo = boton.getAttribute("data-id-articulo");
        const descripcion = document.getElementById(`descri${idArticulo}`);
        // Lógica para abrir el modal
        const idart_modal = document.getElementById('idarts')
        idart_modal.innerText = idArticulo
        const descriart_modal = document.getElementById('descriarts')
        descriart_modal.innerHTML = descripcion.textContent;
        const cantidad = document.getElementById('cantidadMovimientos')
        cantidad.value = ''

        $("#salidaStockModal").modal("show");
    }
});
document.addEventListener("click", function(e) {
    const target = e.target;
    // Verifica si el clic fue en el botón o en un hijo del botón
    if (target.classList.contains("btn-cambiarprecios")) {
        const checkboxes = document.querySelectorAll('.form-check-input');
        var anyselected = false
        // Itera sobre los checkboxes y los marca como 'checked'
        checkboxes.forEach(checkbox => {
            if (checkbox.checked) {
                anyselected = true;
            }
        });
        if (anyselected){
            moverFilasSeleccionadas(); // Llamar a la función que mueve las filas seleccionadas
            $("#exampleModal").modal("show");
        } else {
            alert('Seleccione al menos un Articulo');
        }
    }
});
const guardarPrecioBtn = document.getElementById('guardarprecio');
if (guardarPrecioBtn) {
    guardarPrecioBtn.addEventListener('click', () => {
        const tablaModal = document.getElementById('articulos_sel');
        const articulosActualizados = [];
        const margen = document.getElementById('margenPorcentaje');
        if (margen.value !='0' && margen.value != ''){
            Array.from(tablaModal.rows).forEach((row, rowIndex) => {
            //if (rowIndex === 0) return; // Saltar la fila de encabezado, si existe
    
            const articuloId = row.cells[3].innerText;  
            const nuevoPrecio = parseFloat(row.cells[2].innerText.replace('.', '').replace(',', '.'));  // Suponiendo que el nuevo precio está en la tercera celda y formateado como "9.999,00"
    
            // Agregar artículo a la lista con el ID y el nuevo precio
            articulosActualizados.push({ id: articuloId, nuevo_precio: nuevoPrecio, porcentaje : margen.value });
            });
    
            // Enviar la lista de artículos actualizados al servidor usando AJAX
            fetch('/myapp/actualizar_precios/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')  // Incluye el token CSRF si usas Django
                },
                body: JSON.stringify({ articulos: articulosActualizados })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Cerrar el modal al completar la actualización
                    $('#exampleModal').modal('hide');
                    alert('¡Precios actualizados con éxito!');
                    const btnCambioprecio = document.getElementById('cambioprecio');
                    const margenPorcentaje = document.getElementById('margenPorcentaje');
                    const btnselall = document.getElementById('toggleSeleccion')
                    margenPorcentaje.innerHTML = '0,00'
                    // actualizo dashboard
                    buscart();
                    btnselall.textContent = "Seleccionar Todos"
                } else {
                    alert('Error al actualizar los precios. Por favor, inténtalo de nuevo.');
                }
            })
            .catch(error => console.error('Error al actualizar precios:', error));
        } else {
            alert('Porcentaje de Subida no puede ser 0')
        }
        });
    }

// Función para obtener el token CSRF si usas Django
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const sellect_all = document.getElementById('toggleSeleccion')
if (sellect_all){
    sellect_all.addEventListener('click', () => {
    // Selecciona todos los checkboxes con la clase 'checkbox-row'
        const checkboxes = document.querySelectorAll('.form-check-input');
        const isSelectAll = this.textContent === 'Seleccionar Todos';
        const btnCambioprecio = document.getElementById('cambioprecio');
        // Itera sobre los checkboxes y los marca como 'checked'
        checkboxes.forEach(checkbox => {
            if (checkbox.checked) {
                checkbox.checked = false;
                btnCambioprecio.disabled = true    
            } else {
                checkbox.checked = true;
                btnCambioprecio.disabled = false    
            }
        });
        this.textContent = isSelectAll ? 'Deseleccionar Todos' : 'Seleccionar Todos';
    })
};

document.addEventListener('DOMContentLoaded', (event) => {
    // Ejecutar código cuando el modal se abre
    const modal = document.getElementById('exampleModal');
    if (modal){
        modal.addEventListener('shown.bs.modal', () => {
            moverFilasSeleccionadas(); // Llamar a la función que mueve las filas seleccionadas
        });
    }
});

function moverFilasSeleccionadas() {
    const tablaOriginal = document.getElementById('articulosList');
    const tablaModal = document.getElementById('articulos_sel');
    // Limpia la tabla del modal para evitar duplicados
    tablaModal.innerHTML = "";
    var checked = false 
    // Recorre todas las filas de la tabla original
    Array.from(tablaOriginal.rows).forEach(row => {
        // Encuentra el checkbox en la fila actual
        const checkbox = row.querySelector('.form-check-input');

        // Si el checkbox está seleccionado
        if (checkbox && checkbox.checked) {
            // Crea una nueva fila en la tabla del modal
            const nuevaFila = tablaModal.insertRow();
            checked = true
            // Copia el contenido de las celdas de la fila original
            Array.from(row.cells).forEach((cell, index) => {
                if (index == 1 || index == 2) {  // Excluye la columna del checkbox
                    const nuevaCelda = nuevaFila.insertCell();
                    if (index == 2) {
                        nuevaCelda.style.textAlign = 'right';
                    }
                    nuevaCelda.innerHTML = cell.innerText;
                    if (index == 2) {
                        const nuevaCelda = nuevaFila.insertCell();
                        nuevaCelda.innerHTML = '0.00'
                        nuevaCelda.style.textAlign = 'right';
                    }
                }
                if (index == 12) {
                    const nuevaCelda = nuevaFila.insertCell();
                    nuevaCelda.innerHTML = cell.innerHTML;
                    nuevaCelda.style.display = 'none'
                }
            });
        }
    });
}
function calcula_precio_nuevo() {
    const tablaModal = document.getElementById('articulos_sel');
    const margen = document.getElementById('margenPorcentaje');
    // Limpia la tabla del modal para evitar duplicados
    var precionuevo = 0
    var multi = (margen.value * 0.01) + 1
    // Recorre todas las filas de la tabla original
    Array.from(tablaModal.rows).forEach(row => {
            Array.from(row.cells).forEach((cell, index) => {
                if (index == 1) {
                    const precioOriginal = parseFloat(cell.innerHTML.replace('.', '').replace(',', '.')); // Convertir a número
                    precionuevo = precioOriginal * multi;
                }
                if (index == 2) {  
                    cell.innerHTML = formatNumberToEuropeanStyle(precionuevo)
                }
            });
    });
}
function guardarMovimiento(empresa, id_articulo, tipoMovimiento, motivo, cantidad, precioCompra, numdoc) {
    // Configura los datos a enviar
    const datos = {
        empresa : empresa,
        id_articulo : id_articulo,
        tipo_movimiento: tipoMovimiento,
        motivo: motivo,
        cantidad: cantidad,
        precio_compra: precioCompra,
        numdoc: numdoc
    };
    if (cantidad.value !='0' && cantidad.value != ''){
        // Envía la solicitud a la URL para guardar el movimiento en la base de datos
        fetch('/myapp/guardar_movimiento/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(datos)
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message)
            if (data.modal == 'Regularizacion'){
                $('#regularizaStockModal').modal('hide');
            } else if (data.modal == 'Entrada'){  
                $('#entradaStockModal').modal('hide');
            } else {
                $('#salidaStockModal').modal('hide');
            }    
            buscart();
            // Maneja la respuesta aquí (por ejemplo, cierra el modal y muestra un mensaje)
        })
        .catch(error => {
            console.error('Error:', error);
            // Maneja el error aquí
        });
    } else {
        alert('Cantidad no puede ser 0')
    }
}
document.getElementById('guardarregularizaStock').addEventListener('click', function() {
    const descriart = document.getElementById('descriartr').innerText;
    const tipoMovimiento = 'Regularizacion';
    const id_articulo = document.getElementById('idartr').innerText;
    const motivo = document.getElementById('motivoMovimientor').value;
    const cantidad = document.getElementById('cantidadMovimientor').value;
    if (cantidad != ''){
        const mensaje = `¿Confirmás el movimiento?\n\nTipo: ${tipoMovimiento}\nMotivo: ${motivo}\nCantidad: ${cantidad} para el artículo ${descriart}`;
        if (confirm(mensaje)) {
            guardarMovimiento('0', id_articulo, tipoMovimiento, motivo, cantidad, 0, '');
        }
    } else {
        alert('Entre una cantidad')
    }
});

document.getElementById('guardarentradaStock').addEventListener('click', function() {
    const descriart = document.getElementById('descriarte').innerText;
    const tipoMovimiento = 'Entrada';
    const id_articulo = document.getElementById('idarte').innerText;
    const empresa = document.getElementById('empresaOrigen').innerText;
    const motivo = document.getElementById('motivoMovimientoe').value;
    const cantidad = document.getElementById('cantidadMovimientoe').value;
    const precioCompra = document.getElementById('precioComprae').value;
    const documentoe = document.getElementById('documentoe').value;
    if (cantidad !='0' && cantidad != ''){
        const mensaje = `¿Confirmás el movimiento?\n\nTipo: ${tipoMovimiento}\nMotivo: ${motivo}\nCantidad: ${cantidad} para el artículo ${descriart}`;
        if (confirm(mensaje)) {
            guardarMovimiento(empresa, id_articulo, tipoMovimiento, motivo, cantidad, precioCompra, '');
        }
    } else {
        alert('Cantidad no puede ser 0')
    }
});

document.getElementById('guardarsalidaStock').addEventListener('click', function() {
    const descriart = document.getElementById('descriarts').innerText;
    const tipoMovimiento = 'Salida';
    const id_articulo = document.getElementById('idarts').innerText;
    const empresa = document.getElementById('empresaDestino').innerText;
    const motivo = document.getElementById('motivoMovimientos').value;
    const cantidad = document.getElementById('cantidadMovimientos').value;
    if (cantidad !='0' && cantidad != ''){
        const mensaje = `¿Confirmás el movimiento?\n\nTipo: ${tipoMovimiento}\nMotivo: ${motivo}\nCantidad: ${cantidad} para el artículo ${descriart}`;
        if (confirm(mensaje)) {
            guardarMovimiento(empresa, id_articulo, tipoMovimiento, motivo, cantidad, 0, '');
        }
    } else {
        alert('Cantidad no puede ser 0')
    }
});

function manejar_disabled_compra() {
    const motivo = document.getElementById('motivoMovimientoe').value;
    const empresa = document.getElementById('empresaOrigen');
    const preciocompra = document.getElementById('precioComprae');
    const documentoe = document.getElementById('documentoe');
// Agrega un event listener al select que controla el estado
    // Verifica el valor seleccionado y habilita/deshabilita los campos según corresponda

    if (motivo == 'Compra') {
        empresa.disabled = true;
        preciocompra.disabled = false;
        documentoe.disabled = false;
    } else {
        empresa.disabled = false;
        preciocompra.disabled = true;
        documentoe.disabled = true;
    }
}

function formatNumberToEuropeanStyle(number) {
    // Convertir el número a un string con 2 decimales
    const formattedNumber = number.toFixed(2);
    
    // Reemplazar el punto decimal con una coma
    const parts = formattedNumber.split('.');
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    
    return parts.join(',');
}

$(document).ready(function (){
        var id_empresa = document.getElementById('idempresa').innerText
        familias_empresa(id_empresa);
	});

function ponerfamilia(idfamilia, nomfamilia){
    document.querySelectorAll('#sidebar-nav .sv-fam-item').forEach(i => i.classList.remove('active'));
    document.getElementById('fam' + idfamilia).classList.add('active');
    $('#idfamilia').html(idfamilia);
    $('#familia').html(nomfamilia);
    var idempresa = document.getElementById('idempresa').innerText;
    var nuevoArticuloLink = document.getElementById('nuevoArticulo');
    if (nuevoArticuloLink) {
        nuevoArticuloLink.href = '/myapp/articulo/' + idempresa + '/0/?pfamilia=' + idfamilia
    }
    var nuevoclientesLink = document.getElementById('clientes');
    if (nuevoclientesLink) {
        nuevoclientesLink.href = '/myapp/dashboard/' + idempresa + '/clientes/?pfamilia=' + idfamilia
    }
    var nuevoborrarcarritolink = document.getElementById('borracarrito')
    if (nuevoborrarcarritolink) {
        console.log(idfamilia)
        nuevoborrarcarritolink.href = '/myapp/dashboard/' + idempresa + '/vaciar/?pfamilia=' + idfamilia
    }
    var nuevohomeLink = document.getElementById('home');   
    nuevohomeLink.href = '/myapp/dashboard/' + idempresa + '/?pfamilia=' + idfamilia
    var nuevoventasLink = document.getElementById('ventas');
    var nuevomovimientosLink = document.getElementById('movimientos');
    if (nuevoventasLink) {
        nuevoventasLink.href = '/myapp/dashboard/' + idempresa + '/ventas/?pfamilia=' + idfamilia
        nuevomovimientosLink.href = '/myapp/dashboard/' + idempresa + '/movimientos/?pfamilia=' + idfamilia
    }

    buscart();
}

document.addEventListener('DOMContentLoaded', function () {
    const descriart = document.getElementById('descriartr');
    const modalr = document.getElementById('regularizaStockModal');
    const saveBtnr = document.getElementById('guardarregularizaStock');
    const idfamilia = document.getElementById('idfamilia').innerText;
    const familia = document.getElementById('familia').innerText;
    ponerfamilia(idfamilia, familia);
    const stockInputr = document.getElementById('cantidadMovimientor');

    // Coloca el foco en el input cuando se abre el modal
    modalr.addEventListener('shown.bs.modal', function () {
      stockInputr.focus();
    });
  
    // Escucha cuando se presione una tecla en el modal
    modalr.addEventListener('keydown', function (event) {
      if (event.key === 'Enter') {
        event.preventDefault(); // Evita que el formulario se envíe si es un formulario
        saveBtnr.click(); // Simula el click en el botón "Guardar"
      }
    });

    const modals = document.getElementById('salidaStockModal');
    const saveBtns = document.getElementById('guardarsalidaStock');

    const stockInputs = document.getElementById('cantidadMovimientos');

    // Coloca el foco en el input cuando se abre el modal
    modals.addEventListener('shown.bs.modal', function () {
      stockInputs.focus();
    });
  
    // Escucha cuando se presione una tecla en el modal
    modals.addEventListener('keydown', function (event) {
      if (event.key === 'Enter') {
        event.preventDefault(); // Evita que el formulario se envíe si es un formulario
        saveBtns.click(); // Simula el click en el botón "Guardar"
      }
    });
  });
    