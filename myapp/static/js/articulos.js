function familias_empresa(idempresa, nomempresa){
  $('#navi' + idempresa).add("active");
  $('#empresa').html(nomempresa);
  $('#idempresa').html(idempresa);
  $('#sidebar-nav').html("");
  var idfamilia = document.getElementById('idfamilia').innerHTML;
    $.ajax({
        url:'/myapp/familias/?pfamilia=' + idfamilia,
        data:{
          idempresa: idempresa,
        },
        type:"get",
        datatype: "json",
        success:function(response){
          $('#idfamilia').html(response.id_familia)
          response.filas.forEach(function(item) {
            $('#sidebar-nav').append(item.fila);
          });
          var primera = document.querySelector('#sidebar-nav .sv-fam-item');
          if (primera) primera.classList.add('active');
        },
      });
    buscart()
}

    let debounceTimeout; // Variable para almacenar el temporizador

    function buscart() {
        clearTimeout(debounceTimeout); // Limpiar cualquier temporizador existente
    
        // Establecer un nuevo temporizador para la búsqueda
        debounceTimeout = setTimeout(() => {
            var nombre = document.getElementById('articsearch').value;
            var idfamilia = document.getElementById('idfamilia').innerHTML;
            var id_empresa = document.getElementById('idempresa').innerText;
            $('#articulosList').html(""); // Limpiar la lista de artículos
            $('#loadingIndicator').show();

            $.ajax({
                url: '/myapp/articulos/',
                data: {
                    nombre: nombre,
                    familia: idfamilia,
                    idempresa: id_empresa,
                },
                type: "get",
                datatype: "json",
                success: function(response) {
                  $('#loadingIndicator').hide();
                    for (let i = 0; i < response.length; i++) {
                        $('#articulosList').append(response[i]['fila']);
                    }
                },
            });
        }, 400); // Esperar 300 ms después de que el usuario deje de escribir
    }
        
    document.addEventListener('DOMContentLoaded', function () {
      const precioCompraInput = document.getElementById('id_precio_compra');
      const margenInput = document.getElementById('id_margen');
      const margen2Input = document.getElementById('id_margen2');
      const precioVentaInput = document.getElementById('id_precio_venta');
      const fechaPrecioInput = document.getElementById('id_fecha_precio');
    
      precioCompraInput.addEventListener('input', function () {
        const precioCompra = parseFloat(precioCompraInput.value) || 0;
        const margen = parseFloat(margenInput.value) || 0;
        const margen2 = parseFloat(margen2Input.value) || 0;
        
        const precioVenta = precioCompra * (1 + margen / 100) * (1 + margen2 / 100);
        precioVentaInput.value = precioVenta.toFixed(2);
    
        // Actualiza el campo de fecha_precio con la fecha actual
        const hoy = new Date().toISOString().split('T')[0];
        fechaPrecioInput.value = hoy;

      });
      
      margenInput.addEventListener('input', function () {
        const precioCompra = parseFloat(precioCompraInput.value) || 0;
        const margen = parseFloat(margenInput.value) || 0;
        const margen2 = parseFloat(margen2Input.value) || 0;
        
        const precioVenta = precioCompra * (1 + margen / 100) * (1 + margen2 / 100);
        precioVentaInput.value = precioVenta.toFixed(2);
    
        // Actualiza el campo de fecha_precio con la fecha actual
        const hoy = new Date().toISOString().split('T')[0];
        fechaPrecioInput.value = hoy;

      });
      
      margen2Input.addEventListener('input', function () {
        const precioCompra = parseFloat(precioCompraInput.value) || 0;
        const margen = parseFloat(margenInput.value) || 0;
        const margen2 = parseFloat(margen2Input.value) || 0;
        
        const precioVenta = precioCompra * (1 + margen / 100) * (1 + margen2 / 100);
        precioVentaInput.value = precioVenta.toFixed(2);
    
        // Actualiza el campo de fecha_precio con la fecha actual
        const hoy = new Date().toISOString().split('T')[0];
        fechaPrecioInput.value = hoy;

      });
    });
  