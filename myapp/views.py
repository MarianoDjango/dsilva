from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
# Create your views here.
from .models import empresas, familias, articulos, hist_movart, tipomovimientos, formaspago, clientes, cabecera_venta
import json
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from .forms import articulosForm, clientesForm
from datetime import datetime, timedelta, time, timezone as dt_timezone
from decimal import Decimal
from django.urls import reverse
from django.db import transaction
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import make_aware, now
import os
from zipfile import ZipFile
import requests
from django.core.files.base import ContentFile
from django.conf import settings
from django.templatetags.static import static
import subprocess
import glob
import cloudinary.uploader
from django.utils.text import slugify
from django.http import HttpResponse
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from io import BytesIO

def index(request):
    return render(request, 'index.html')

def landing_preview(request):
    return render(request, 'index_new.html')

'''def nosotros(request):
    return render(request, 'nosotros.html')'''

def afterlogin( request, *args, **kwargs):
    idempresa = request.user.perfil.idempresa
    urlredirect = "/myapp/dashboard/" + str(idempresa.id) + '/?pfamilia=0'
    return redirect(urlredirect)

@login_required
def famlias_empresa(request, **kwargs):
    empresa_id = request.GET['idempresa']
    familias_var = familias.objects.filter(idempresa=empresa_id)
    id_familia = request.GET['pfamilia']
    recs = []
    for fam in familias_var:
        carpeta = fam.nombre
        cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME')
        imagen_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/dsilva/{fam.nombre}/generic.jpg"
        fila = f'<a id="fam{fam.id}" href="javascript:void(0);" class="sv-fam-item" onclick="ponerfamilia({fam.id}, \'{fam.nombre}\')"><div class="sv-fam-img"><img src="{imagen_url}" onerror="this.style.display=\'none\'"></div><span class="sv-fam-name">{fam.nombre}</span></a>'
        recs.append({'fila': fila})
    fila = f'<a id="fam{0}" href="javascript:void(0);" class="sv-fam-item" onclick="ponerfamilia({0}, \'Todos\')"><div class="sv-fam-img"></div><span class="sv-fam-name">Todos</span></a>'    
    recs.append({'fila': fila})
    data = {'filas' : recs,
            'id_familia' : id_familia}
    return JsonResponse(data)

@login_required
def articulos_famila(request, **kwargs):
    recs = []
    json_list = {}
    #if request.user.is_authenticated:
    familia_id = request.GET['familia']
    nombre_var = request.GET['nombre']
    idempresa_var = request.GET['idempresa']
    empresa_obj = get_object_or_404(empresas, id=idempresa_var)
    if familia_id != '0':
        if nombre_var == "":
            articles = articulos.objects.filter(idempresa=idempresa_var, familia=familia_id, activo=True).values('id', 'idempresa','descripcion', 'precio_venta', 'fecha_precio', 'stock', 'fecha_stock', 'familia', 'precio_compra', 'activo')
        else:
            articles = articulos.objects.filter(idempresa=idempresa_var, familia=familia_id, descripcion__icontains=nombre_var, activo=True).values('id', 'idempresa','descripcion', 'precio_venta', 'fecha_precio', 'stock', 'fecha_stock', 'familia', 'precio_compra', 'activo')
    else:
        if nombre_var == "":
            articles = articulos.objects.filter(idempresa=idempresa_var).values('id', 'idempresa','descripcion', 'precio_venta', 'fecha_precio', 'stock', 'fecha_stock', 'familia', 'precio_compra', 'activo')
        else:
            articles = articulos.objects.filter(idempresa=idempresa_var, descripcion__icontains=nombre_var).values('id', 'idempresa','descripcion', 'precio_venta', 'fecha_precio', 'stock', 'fecha_stock', 'familia', 'precio_compra', 'activo')


    #familia = familias.objects.get(id=int(familia_id))
    recs.append(json_list)
    for articulo in articles:
        fila = '<tr style="cursor:hand;">'
        #if articulo['idempresa'] == request.user.perfil.idempresa.id:
        if request.user.is_staff:
            id_articulo = str(articulo['id'])
            fila += f'<td class="text-center"><div class="form-check"><input class="form-check-input" type="checkbox" value="" id="flexCheckDefault{id_articulo}"><label class="form-check-label" for="flexCheckDefault{id_articulo}"></label></div></td>'
            if articulo['activo']:
                fila += '<td><a href="../../articulo/' + idempresa_var + '/' + str(articulo['id']) + '/?pfamilia=' + str(articulo['familia']) + '" id="descri' + str(articulo['id']) + '">' + articulo['descripcion'] + '</a></td>'
            else:
                fila += '<td><a href="../../articulo/' + idempresa_var + '/' + str(articulo['id']) + '/?pfamilia=' + str(articulo['familia']) + '" id="descri' + str(articulo['id']) + '" style="color:red">' + articulo['descripcion'] + '</a></td>'
            fila += '<td class="text-end">' + '{:,.2f}'.format(articulo['precio_venta']).replace(",", "@").replace(".", ",").replace("@", ".") + '</td>'
            fila += '<td class="text-center">' + str(articulo['fecha_precio'].strftime('%d-%b-%Y').lower()) + '</td>'
            fila += '<td class="text-end">' +  '{:,.2f}'.format(articulo['stock']).replace(",", "@").replace(".", ",").replace("@", ".") + '</button></td>'
            fila += '<td class="text-center">' + str(articulo['fecha_stock'].strftime('%d-%b-%Y').lower()) + '</td>'
            if empresa_obj.venta:
                if articulo['stock'] == 0 or not articulo['activo']:
                    fila += f'<td class="text-center"><input type="text" class="form-control cantidad-plus" style="border-radius: 10px;" placeholder="Sin Stock" readonly></td>'
                    fila += f'<td class="text-center"><button class="btn btn-secondary agregar-carrito" data-id="'+ str(articulo['id']) + '" title="Agregar al Pedido" disabled><i class="bi bi-cart-plus"></i></button></td>'
                else:
                    fila += f'<td class="text-center"><input type="text" class="form-control cantidad-plus" style="border-radius: 10px;" placeholder="Cant."></td>'
                    fila += f'<td class="text-center"><button class="btn agregar-carrito" data-id="'+ str(articulo['id']) + '" style="background-color: #92dea3;" title="Agregar al Pedido"><i class="bi bi-cart-plus"></i></button></td>'
            if articulo['activo']:
                fila += f'<td class="text-end"><button class="btn btn-success entrada-stock" title="Entrada Stock" data-id-articulo="' +  id_articulo + '" data-toggle="modal" data-target="#movimientoStockModal"><i class="bi bi-window-plus"></i></button></td>'
            else:
                fila += f'<td class="text-end"><button class="btn btn-secondary entrada-stock" title="Entrada Stock" data-id-articulo="' +  id_articulo + '" data-toggle="modal" data-target="#movimientoStockModal" disabled><i class="bi bi-window-plus"></i></button></td>'
            if articulo['stock'] == 0 or not articulo['activo']:
                fila += f'<td class="text-end"><button class="btn btn-secondary salida-stock" title="Salida Stock" data-id-articulo="' +  id_articulo + '" data-toggle="modal" data-target="#movimientoStockModal" disabled><i class="bi bi-window-dash"></i></button></td>'
            else:
                fila += f'<td class="text-end"><button class="btn btn-danger salida-stock" title="Salida Stock" data-id-articulo="' +  id_articulo + '" data-toggle="modal" data-target="#movimientoStockModal"><i class="bi bi-window-dash"></i></button></td>'
            if articulo['activo']:
                fila += f'<td class="text-end"><button class="btn btn-secondary actualizar-stock" title="Regularizar Stock" data-id-articulo="' +  id_articulo + '" data-toggle="modal" data-target="#movimientoStockModal"><i class="bi bi-boxes"></i></button></td>'
            else:
                fila += f'<td class="text-end"><button class="btn btn-secondary actualizar-stock" title="Regularizar Stock" data-id-articulo="' +  id_articulo + '" data-toggle="modal" data-target="#movimientoStockModal" disabled><i class="bi bi-boxes"></i></button></td>'
            fila += '<td class="text-center preciocompra" style="display : none;">' + '{:,.2f}'.format(articulo['precio_compra']).replace(",", "@").replace(".", ",").replace("@", ".") + '</td>'
        else:
            if articulo['activo']:
                fila += '<td>'+ articulo['descripcion'] + '</td>'
            else:
                fila += '<td style="color:red;">'+ articulo['descripcion'] + '</td>'
            fila += '<td class="text-end">{:,.2f}'.format(articulo['precio_venta']).replace(",", "@").replace(".", ",").replace("@", ".") + '</td>'
            fila += '<td class="text-center">' + str(articulo['fecha_precio']) + '</td>'
            fila += '<td class="text-end">{:,.2f}'.format(articulo['stock']).replace(",", "@").replace(".", ",").replace("@", ".") + '</td>'
            fila += '<td class="text-center">' + str(articulo['fecha_stock']) + '</td>'
            if empresa_obj.venta:
                if articulo['idempresa'] == request.user.perfil.idempresa.id:
                    if articulo['stock'] == 0 or not articulo['activo']:
                        fila += f'<td class="text-center"><input type="text" class="form-control cantidad-plus" style="border-radius: 10px;" placeholder="Sin Stock" readonly></td>'
                        fila += f'<td class="text-center"><button class="btn btn-secondary agregar-carrito" data-id="'+ str(articulo['id']) + '" title="Agregar al Pedido" disabled><i class="bi bi-cart-plus"></i></button></td>'
                    else:
                        fila += f'<td class="text-center"><input type="text" class="form-control cantidad-plus" style="border-radius: 10px;" placeholder="Cant."></td>'
                        fila += f'<td class="text-center"><button class="btn agregar-carrito" data-id="'+ str(articulo['id']) + '" style="background-color: #92dea3;" title="Agregar al Pedido"><i class="bi bi-cart-plus"></i></button></td>'

        fila += '<td class="text-center" style="display : none;">' + str(articulo['id']) + '</td></tr>'
        json_list = {
            'fila': fila,
        }
        recs.append(json_list)

    data = json.dumps(recs)
    return HttpResponse(data, 'application/json')

@login_required
def clientes_empresa(request, **kwargs):
    recs = []
    json_list = {}
    #if request.user.is_authenticated:
    nombre_var = request.GET['nombre']
    idempresa_var = request.GET['id_empresa']
    pfamilia = request.GET['pfamilia']
    empresa_obj = get_object_or_404(empresas, id=idempresa_var)
    if nombre_var == "":
        clientes_qry = clientes.objects.filter(idempresa=empresa_obj, activo=True).values('id', 'idempresa','nombre', 'apellido', 'email', 'telefono')
    else:
        clientes_qry = clientes.objects.filter(idempresa=empresa_obj, nombre__icontains=nombre_var, activo=True).values('id', 'idempresa','nombre', 'apellido', 'email', 'telefono')
    recs.append(json_list)
    for cliente in clientes_qry:
        fila = '<tr style="cursor:hand;">'
        if cliente['idempresa'] == request.user.perfil.idempresa.id or request.user.is_staff:
            id_cliente = str(cliente['id'])
            fila += '<td><a href="' + id_cliente + '/?pfamilia=' + pfamilia + '" id="descri' + id_cliente + '">' + cliente['nombre'] + '</a></td>'
        else:
            fila += '<td>' + cliente['nombre'] + '</td>'
        fila += '<td class="text-center">' + cliente['apellido'] + '</td>'
        fila += '<td class="text-center">' + str(cliente['email']) + '</td>'
        if (cliente['telefono']):
            fila += '<td class="text-end">' +  cliente['telefono'] + '</td>'
        fila += '<td class="text-center" style="display : none;">' + str(cliente['id']) + '</td>'
        json_list = {
            'fila': fila,
        }
        recs.append(json_list)

    data = json.dumps(recs)
    return HttpResponse(data, 'application/json')

class clientes_view(LoginRequiredMixin,View):
    template_name = 'myapp/clientes.html'

    def get(self, request, *args, **kwargs):
        id_familia = request.GET['pfamilia']
        empresa_id = kwargs['id_empresa']
        empresa_obj = get_object_or_404(empresas, id=empresa_id)
        context = {'id_empresa':int(empresa_id),
                    'nomempresa' : empresa_obj.name,
                    'id_familia': id_familia
                }
        return render(self.request, self.template_name, context)

class dashboard_view(LoginRequiredMixin,View):
    template_name = 'myapp/dashboard.html'
    login_url = '/accounts/login/'

    def get(self, request, *args, **kwargs):
        empresa_id = kwargs['id_empresa']
        pfamilia = request.GET['pfamilia']
        empresa_obj = get_object_or_404(empresas, id=empresa_id)
        carrito = request.session.get(f'carrito_{empresa_id}', {})
        cantidad_total = sum(item['cantidad'] for item in carrito.values())

        companies_var = empresas.objects.all()  # Obtenemos todas las empresas
        empresa_user = self.request.user.perfil.idempresa.id
        nomempresa_user = self.request.user.perfil.idempresa.name
        familias_var = familias.objects.filter(idempresa=empresa_id)
        if pfamilia and pfamilia != '0':
            familia = familias_var.get(id=pfamilia)
        else:
            familia = familias_var[0]

        motivos_entrada = tipomovimientos.objects.filter(tipo='entrada')
        motivos_salida = tipomovimientos.objects.filter(tipo='salida').exclude(motivo='venta')
        motivos_regularizacion = tipomovimientos.objects.filter(tipo='regularizacion')

        context = {'empresas': companies_var,
                    'id_empresa':int(empresa_id),
                    'nomempresa' : empresa_obj.name,
                    'id_familia' : familia.id,
                    'familia_nom' : familia.nombre,
                    'motivos_entrada': motivos_entrada,
                    'motivos_salida': motivos_salida,
                    'motivos_regularizacion': motivos_regularizacion,
                    'cantidad_carrito' : cantidad_total
        }

        return render(self.request, self.template_name, context)

@login_required
def articulo_create_or_update(request, **kwargs):
    #if request.user.is_authenticated:
        pfamilia = request.GET.get('pfamilia')

        if request.user.is_staff:
            if kwargs['pk'] != '0':
                articulo = get_object_or_404(articulos, pk=kwargs['pk'])
                precio_venta_anterior = articulo.precio_venta
                empresa = articulo.idempresa
                empresa_imagenes = articulo.idempresa.imagenes
            else:
                articulo = articulos()
                articulo.fecha_precio = datetime.today()
                articulo.fecha_stock = datetime.today()
                precio_venta_anterior = None
                empresa = empresas.objects.get(id=int(kwargs['id_empresa']))
                empresa_imagenes = empresa.imagenes
                articulo.idempresa = empresa

            if request.method == 'POST':
                '''cloudinary.config(
                    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
                    api_key=os.getenv('CLOUDINARY_API_KEY'),
                    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
                    secure=True
                )'''

                form = articulosForm(request.POST, request.FILES, instance=articulo)
                if form.is_valid():
                    is_new = form.instance.pk is None
                    if is_new:
                        tipo_mov = 'Creacion Articulo'
                        precio_venta_anterior = 0
                    else:
                        tipo_mov = 'Actualiza Articulo'

                    articulo = form.save(commit=False)

                    estado = request.POST.get("imagen_estado")

                    # Eliminar anterior si hay que reemplazar
                    if estado in ["archivo", "url", "reestablecer"] and articulo.imagen_cloud:
                        cloudinary.uploader.destroy(articulo.imagen_cloud.public_id)

                    if estado == "archivo":
                        archivo = request.FILES.get("imagen_file")
                        if archivo:
                            result = cloudinary.uploader.upload(
                                archivo,
                                folder=f"dsilva/{articulo.familia.nombre}",
                                public_id=f"dsilva/{articulo.familia.nombre.strip()}/{articulo.descripcion.strip()}",
                                overwrite=True
                            )
                            articulo.imagen_cloud = result['public_id']

                    elif estado == "url":
                        imagen_url = request.POST.get("imagen_url")
                        if imagen_url:
                            response = requests.get(imagen_url)
                            if response.status_code == 200:
                                result = cloudinary.uploader.upload(
                                    ContentFile(response.content),
                                    folder=f"dsilva/{articulo.familia.nombre}",
                                    public_id=f"dsilva/{articulo.familia.nombre}/{articulo.descripcion}",
                                    overwrite=True
                                )
                                articulo.imagen_cloud = result['public_id']

                    elif estado == "reestablecer":
                        articulo.imagen_cloud = None
                                            
                    articulo.save()
                    #print(art_val_ant)
                    if (precio_venta_anterior != articulo.precio_venta) or is_new:
                        historico = hist_movart( articulo = articulo,
                                    fechamov = datetime.today(),
                                    tipomov = tipo_mov,
                                    numdoc = '0',
                                    cantidad = 0,
                                    precioactual = precio_venta_anterior,
                                    porprecio = 0,
                                    nuevoprecio = articulo.precio_venta,
                                    stockactual = articulo.stock,
                                    nuevostock = articulo.stock,
                                    usuario = request.user
                                )
                        historico.save()

                    urlredirect = "/myapp/dashboard/" + kwargs['id_empresa'] +'?pfamilia=' + str(articulo.familia.id)
                    return redirect(urlredirect)
            else:
                families = familias.objects.filter(idempresa=empresa)
                if pfamilia == '0':
                    familia = families[0]
                else:
                    familia = families.get(id=pfamilia)

                articulo.familia = familia
                #articulo.fecha_precio = datetime.datetime.today().date()
                #articulo.fecha_stock = datetime.datetime.today().date()
                form = articulosForm(instance=articulo, empresa_id=int(kwargs['id_empresa']))

            return render(request, 'myapp/articulo_form.html', {'form': form, 'id_empresa':kwargs['id_empresa'], 'id_familia': familia.id, 'DEFAULT_IMAGE': static(settings.DEFAULT_IMAGE), 'imagenes': empresa_imagenes})
        else:
            return render(request, 'myapp/articulo_form.html')
    #return redirect('login')

@login_required
def cliente_create_or_update(request, **kwargs):
        pfamilia = request.GET.get('pfamilia')
    #if request.user.is_authenticated:
        if request.user.perfil.idempresa.id == int(kwargs['id_empresa']) or request.user.is_staff:
            if kwargs['pk'] != '0':
                cliente = get_object_or_404(clientes, pk=kwargs['pk'])
            else:
                cliente = clientes()

            if request.method == 'POST':
                form = clientesForm(request.POST, instance=cliente)
                if form.is_valid():
                    form.save()
                    urlredirect = "/myapp/dashboard/" + str(request.user.perfil.idempresa.id) +'/clientes/?pfamilia=' + pfamilia
                    return redirect(urlredirect)
            else:
                empresa = empresas.objects.get(id=int(kwargs['id_empresa']))
                cliente.idempresa = empresa
                cliente.fecha_registro = datetime.today().date()

                form = clientesForm(instance=cliente, empresa_id=int(kwargs['id_empresa']))
        else:
            form = None
        return render(request, 'myapp/cliente_form.html', {'form': form, 'id_empresa':kwargs['id_empresa'], 'id_familia':pfamilia})

@login_required
def actualizar_precios(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        articulos_var = data.get('articulos', [])

        for articulo_data in articulos_var:
                articulo = articulos.objects.get(pk=articulo_data['id'])
                histo_mov = hist_movart()
                histo_mov.articulo = articulo
                histo_mov.fechamov = datetime.today().date()
                tipo_mov = 'Actualizacion precio'
                histo_mov.tipomov = tipo_mov
                histo_mov.precioactual = articulo.precio_venta
                histo_mov.porprecio = articulo_data['porcentaje']
                histo_mov.nuevoprecio = articulo_data['nuevo_precio']

                histo_mov.usuario = request.user
                histo_mov.save()

                articulo.precio_venta = articulo_data['nuevo_precio']
                articulo.fecha_precio = datetime.today().date()
                articulo.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

@login_required
def guardar_movs_stock(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        empresa = data.get('empresa')
        idarticulo_var = data.get('id_articulo')
        tipomov_var = data.get('tipo_movimiento')
        motivo_var = data.get('motivo')
        cantidad_var = data.get('cantidad')
        preciocompra_var = data.get('precio_compra')
        numdoc_var = data.get('numdoc')

        articulo = articulos.objects.get(pk=idarticulo_var)
        histo_mov = hist_movart()
        #empresa_obj = empresas.objects.get(name=empresa)
        histo_mov.empresa = articulo.idempresa
        histo_mov.articulo = articulo
        histo_mov.fechamov = datetime.now()
        mensaje = 'ATENCION!! Cantidad Entrada = 0, no se realizo ningun cambio'
        if cantidad_var !='':
            if tipomov_var == 'Regularizacion':
                mensaje = 'Regularizacion de stock realizada con exito!'
                histo_mov.tipomov = motivo_var
                histo_mov.cantidad = cantidad_var
                histo_mov.stockactual = articulo.stock
                histo_mov.nuevostock = cantidad_var
                histo_mov.usuario = request.user
                histo_mov.save()

                articulo.stock = cantidad_var
                articulo.fecha_stock = datetime.today().date()
                articulo.save()
            elif tipomov_var == 'Entrada':
                mensaje = 'Entrada de stock realizada con exito!'
                histo_mov.tipomov = motivo_var
                histo_mov.cantidad = cantidad_var
                histo_mov.usuario = request.user
                histo_mov.stockactual = articulo.stock
                histo_mov.nuevostock = Decimal(cantidad_var) + articulo.stock
                histo_mov.usuario = request.user
                if motivo_var == "Compra":
                    histo_mov.numdoc = numdoc_var
                    histo_mov.precioactual = articulo.precio_compra
                    histo_mov.nuevoprecio = preciocompra_var

                    articulo.precio_compra = preciocompra_var
                    articulo.fecha_precio = datetime.today().date()
                    articulo.precio_venta = Decimal(preciocompra_var) * (1 + articulo.margen / 100) * (1 + articulo.margen2 / 100)
                elif 'Traspaso' in motivo_var:
                    histo_mov.numdoc = empresa #este campo representa numero tique venta o numero de remito o factura de compra o nombre de empresa en caso de traspasos
                histo_mov.save()

                articulo.stock = Decimal(cantidad_var) + articulo.stock
                articulo.fecha_stock = datetime.today().date()
                articulo.save()
            elif tipomov_var == 'Salida':
                if Decimal(cantidad_var) <= articulo.stock:
                    mensaje = 'Salida de stock realizada con exito!'
                    histo_mov.tipomov = motivo_var
                    histo_mov.numdoc = empresa #este campo representa numero tique venta o numero de remito o factura de compra o nombre de empresa en caso de traspasos
                    histo_mov.cantidad = cantidad_var
                    histo_mov.stockactual = articulo.stock
                    histo_mov.nuevostock = articulo.stock - Decimal(cantidad_var)
                    histo_mov.usuario = request.user
                    histo_mov.save()

                    articulo.stock = articulo.stock - Decimal(cantidad_var)
                    articulo.fecha_stock = datetime.today().date()
                    articulo.save()
                else:
                    mensaje = 'Stock Insuficiente!'
                    return JsonResponse({'success': False, 'modal': tipomov_var, 'message': mensaje})
            return JsonResponse({'success': True, 'modal': tipomov_var, 'message': mensaje})
        return JsonResponse({'success': True, 'modal': tipomov_var, 'message': mensaje})
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

@login_required
def restar_al_carrito(request, articulo_id, **kwargs):
    articulo = get_object_or_404(articulos, id=articulo_id)
    id_empresa = kwargs['id_empresa']

    # Obtener el carrito de la sesión, o inicializarlo si no existe
    carrito = request.session.get(f'carrito_{id_empresa}', {})
    data = json.loads(request.body)
    cantidad_table = int(data.get('cantidad', 1))  # Valor por defecto es 1
    success = True
    # Si el artículo ya está en el carrito, incrementar la cantidad
    if str(articulo_id) in carrito:
        new_cant_carrito = carrito[str(articulo_id)]['cantidad'] - cantidad_table
        if new_cant_carrito >= 0:
            carrito[str(articulo_id)]['cantidad'] -= cantidad_table
        else:
            carrito[str(articulo_id)]['cantidad'] = 0
    else:
        success = False
    # Asegúrate de que la clave sea una cadena de caracteres
    if success:
        carrito[str(articulo_id)]['total_linea'] = carrito[str(articulo_id)]['cantidad'] * carrito[str(articulo_id)]['precio']

    # Guardar el carrito en la sesión
    request.session[f'carrito_{id_empresa}'] = carrito

    # Calcular el total del carrito
    total_carrito = sum(item['total_linea'] for item in carrito.values())

    request.session[f'total_carrito_{id_empresa}'] = total_carrito

    request.session.modified = True
    cantidad_total = sum(item['cantidad'] for item in carrito.values())
    new_cant_art_carrito = carrito[str(articulo_id)]['cantidad']
    new_total_linea = carrito[str(articulo_id)]['total_linea']
    return JsonResponse({'success': success, 'new_cantidad_art': new_cant_art_carrito, 'cantidad_total': cantidad_total, 'new_total_linea' : '{:.2f}'.format(new_total_linea), 'subtotalcarrito' : total_carrito})

@login_required
def agregar_al_carrito(request, articulo_id, **kwargs):
    articulo = get_object_or_404(articulos, id=articulo_id)
    id_empresa = kwargs['id_empresa']
    empresa = empresas.objects.get(id=id_empresa)

    # Obtener el carrito de la sesión, o inicializarlo si no existe
    carrito = request.session.get(f'carrito_{id_empresa}', {})
    data = json.loads(request.body)
    cantidad_table = float(data.get('cantidad', 1))  # Valor por defecto es 1
    success = True
    new_cant_art_carrito = 0
    new_total_linea = 0
    # Si el artículo ya está en el carrito, incrementar la cantidad
    if str(articulo_id) in carrito:
        new_cant_carrito = carrito[str(articulo_id)]['cantidad'] + cantidad_table
        if articulo.stock >= new_cant_carrito:
            carrito[str(articulo_id)]['cantidad'] += cantidad_table
        else:
            success = False
    else:
        if articulo.stock >= cantidad_table:
            # Si no, agregar el artículo al carrito
            carrito[str(articulo_id)] = {
                'nombre': articulo.descripcion,
                'precio': float(articulo.precio_venta),
                'cantidad': cantidad_table,
                'total_linea': articulo.precio_venta
            }
        else:
            success = False
    # Asegúrate de que la clave sea una cadena de caracteres
    if success:
        carrito[str(articulo_id)]['total_linea'] = carrito[str(articulo_id)]['cantidad'] * carrito[str(articulo_id)]['precio']

        # Guardar el carrito en la sesión
    request.session[f'carrito_{id_empresa}'] = carrito

        # Calcular el total del carrito
    total_carrito = sum(item['total_linea'] for item in carrito.values())
    request.session[f'total_carrito_{id_empresa}'] = total_carrito

    request.session.modified = True
    cantidad_total = sum(item['cantidad'] for item in carrito.values())
    if str(articulo_id) in carrito:
        new_cant_art_carrito = carrito[str(articulo_id)]['cantidad']
        new_total_linea = carrito[str(articulo_id)]['total_linea']

    return JsonResponse({'success': success, 'new_cantidad_art': new_cant_art_carrito, 'cantidad_total': cantidad_total, 'new_total_linea' : '{:.2f}'.format(new_total_linea), 'subtotalcarrito' : total_carrito})
    #return redirect('dashboard', id_empresa)  # Redirigir a la página de lista de artículos o carrito
# views.py

@login_required
def quitar_art_de_carrito(request, articulo_id, **kwargs):
    id_empresa = kwargs['id_empresa']
    empresa = empresas.objects.get(id=id_empresa)

    # Obtener el carrito de la sesión, o inicializarlo si no existe
    carrito = request.session.get(f'carrito_{id_empresa}', {})
    success = True
    # Si el artículo ya está en el carrito, incrementar la cantidad
    if str(articulo_id) in carrito:
        del carrito[str(articulo_id)]
    else:
        success = False
    # Asegúrate de que la clave sea una cadena de caracteres
    # Guardar el carrito en la sesión

    # Calcular el total del carrito
    total_carrito = sum(item['total_linea'] for item in carrito.values())
    cantidad_total = sum(item['cantidad'] for item in carrito.values())
    request.session[f'total_carrito_{id_empresa}'] = total_carrito
    request.session.modified = True
    return JsonResponse({'success': success, 'cantidad_total': cantidad_total, 'subtotalcarrito' : total_carrito})

@login_required
def cantidad_total_carrito(request, **kwargs):
    id_empresa = kwargs['id_empresa']
    carrito = request.session.get(f'carrito_{id_empresa}', {})
    cantidad_total = sum(item['cantidad'] for item in carrito.values())
    return JsonResponse({'cantidad_carrito': cantidad_total})

@login_required
def ver_carrito(request, **kwargs):
    id_empresa = kwargs['id_empresa']
    pfamilia = request.GET['pfamilia']
    carrito = request.session.get(f'carrito_{id_empresa}', {})
      # Lógica para obtener el descuento por pago en efectivo
    total = calcular_total_carrito(carrito)  # Lógica para calcular el total
    empresa_id = kwargs['id_empresa']
    empresa_obj = get_object_or_404(empresas, id=empresa_id)
    descuento_efectivo = empresa_obj.dtoefectvo
    formas_pago = formaspago.objects.all()
    cliente_list = clientes.objects.filter(idempresa=id_empresa, activo=True)
    if request.method == 'POST':
        # Manejar el formulario de cierre de venta
        metodo_pago = request.POST.get('payment_method')
        descuento_adicional = request.POST.get('descuento_adicional')
        cerrar_venta(carrito, metodo_pago, descuento_adicional)  # Lógica para cerrar la venta
        return HttpResponseRedirect(reverse('venta_confirmada'))  # Redirigir a una página de confirmación

    return render(request, 'myapp/carrito.html', {
        'carrito': carrito,
        'descuento_efectivo': descuento_efectivo,
        'total': str(total).replace(',','.'),
        'id_empresa' : empresa_id,
        'nombre_empresa' : empresa_obj.name,
        'formas_pago' : formas_pago,
        'dtoefectvo' : empresa_obj.dtoefectvo,
        'clientes' : cliente_list,
        'id_familia': pfamilia
    })

@login_required
def vaciar_carrito(request, id_empresa):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    # Vaciar el carrito de la sesión
    request.session[f'carrito_{id_empresa}'] = {}
    request.session[f'total_carrito_{id_empresa}'] = 0
    request.session.modified = True
    pfamilia = request.GET.get('pfamilia')
    previous_url = request.META.get('HTTP_REFERER')
    if previous_url:
        # Redirigir a la URL anterior, sin 'vaciar/'
        previous_url = previous_url.split('?')[0]
        new_url = f'{previous_url}?pfamilia={pfamilia}'
        return redirect(new_url)

    return redirect('dashboard', id_empresa)
@login_required
def obtener_descuento_efectivo():
    # Lógica para obtener el descuento por pago en efectivo
    return 10  # Ejemplo de valor fijo

def calcular_total_carrito(carrito):
    total = sum(item['precio'] * item['cantidad'] for item in carrito.values())
    return total  # Aplica descuentos aquí si es necesario

@login_required
def imprime_presup(request, **kwargs):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    if request.method == 'POST':
        id_empresa = kwargs['id_empresa']
        carrito = request.session.get(f'carrito_{id_empresa}', {})
        if carrito:
            empresa = get_object_or_404(empresas, id=id_empresa)


            data = json.loads(request.body)
            fpago = data.get('formapago', [])
            formapago = get_object_or_404(formaspago, id=fpago)
            descripcion_forma_pago = formapago.get_tipo_display()
            destoadicional = float(data.get('descuentoAdicional', []))
            subtotal = data.get('subtotal', [])
            total = data.get('total', [])
            cliente = data.get('cliente', [])
            tel_cliente = ''
            dir_cliente = ''
            try:
                cliente_obj = get_object_or_404(clientes, nombre=cliente, idempresa=id_empresa)
                cliente = cliente_obj.nombre + ' ' + cliente_obj.apellido
                tel_cliente = cliente_obj.telefono
                dir_cliente = cliente_obj.direccion + ' - ' + cliente_obj.ciudad + ' - ' + cliente_obj.provincia
            except:
                pass
            success = True
            if descripcion_forma_pago == 'Efectivo':
                dtoeftvo = empresa.dtoefectvo
            else:
                dtoeftvo = 0
            detalle_html = ''
            footer_html = ''
            #try:
                # Inicia una transacción atómica
                #with transaction.atomic():
                    # Crear la cabecera de la venta
                    #cabecera = cabecera_venta.objects.create(fechav=datetime.date.today(),
                    #        cliente = cliente, formapago = formapago, subtotal = subtotal,
                    #        dtoeftvo = dtoeftvo, otrodto = destoadicional, imptotal=total)

            tfechav = datetime.today().strftime(('%d-%m-%Y'))
            timp_dtoadi = subtotal * (destoadicional * 0.01 + 1) - subtotal
            timp_dtoadif = f"{timp_dtoadi:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            if descripcion_forma_pago == 'Efectivo':
                timp_dtoeft = subtotal * (float(empresa.dtoefectvo) * 0.01 + 1) - subtotal
                timp_dtoeftf = f"{timp_dtoeft:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            else:
                timp_dtoeftf = '0.00'

            subtotalf = f"{subtotal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            totalf = f"{total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            cabecera_html = f"""
                <html>
                    <head>
                        <title>Ticket</title>
                        <style>
                            body {{
                                font-family: Verdana, Geneva, sans-serif;
                                font-size: 10px;
                            }}
                            p{{
                                font-size: 10px;
                            }}
                            h3 {{
                                font-size: 12px;
                                font-weight: bold;
                            }}
                            .bold {{
                                font-weight: bold;
                            }}
                            .small {{
                                font-size: 10px;
                            }}
                            .xsmall {{
                                font-size: 6px;
                            }}
                            img {{
                                width: 200px;
                                height: 45px;
                                display: block;
                                margin: 0 auto; /* Centrará la imagen horizontalmente */
                            }}
                            subcab {{
                                font-sze : 6px;
                                width: 220px;
                                height: 6px;
                                display: block;
                                margin: 0 auto; /* Centrará la imagen horizontalmente */
                                text-align: center;
                            }}
                            footer {{
                                font-size : 8px;
                                width: 250px;
                                height: 10px;
                                display: block;
                                margin: 0 auto; /* Centrará la imagen horizontalmente */
                                text-align: center;
                            }}
                            table {{
                                width: 100%;
                                border-collapse: collapse;
                            }}
                            th, td {{
                                padding: 1px;
                                font-size: 8px;
                            }}
                            .left-align {{
                                text-align: left;
                            }}
                            .right-align {{
                                text-align: right;
                            }}
                            th {{
                                text-align: center; /* Centrar los encabezados por defecto */
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="row align-items-center">
                            <img src="{'/static/img/logo.png'}" alt="Logo">
                        </div>
                        <subcab class="xsmall">{empresa.linea1}</subcab>
                        <subcab class="xsmall">{empresa.linea2}</subcab>
                        <subcab class="small">{empresa.linea3}</subcab>
                        <p></p>
                        <hr/>
                        <p><span class="medium bold">Presupuesto</span></p>
                        <p></p>
                        <p><span class="small bold">Fecha: </span>{tfechav}</p>
                        <hr/>
                        <p><span class="small bold">Cliente: </span>{cliente}</p>
                        <p><span class="small bold">Telefono: </span>{tel_cliente}</p>
                        <p><span class="small bold">Dirección: </span>{dir_cliente}</p>
                        <hr/>
                        <table>
                            <thead>
                                <tr>
                                    <th class="small">Artículo</th>
                                    <th class="small">Cant.</th>
                                    <th class="small">Precio</th>
                                    <th class="small">Subtotal</th>
                                </tr>
                            </thead>
                            <p></p>
                            <tbody>
                            <td colspan="4" class="table-active"><hr/></td>
                        """
                    # Iterar a través de las líneas y crearlas
            for item in carrito.items():
                #sum(item['cantidad'] for item in carrito.values())
                articulo_id = item[0]
                nombre_art = item[1]['nombre']
                cantidad = item[1]['cantidad']
                precio_unitario = str(item[1]['precio'])
                total_linea = str(item[1]['total_linea'])
                        # Recuperar el artículo
                articulo = get_object_or_404(articulos, id=articulo_id)

                        # Calcula el subtotal para la línea
                detalle_html += f"""
                    <tr><td class="left-align">{nombre_art}</td>
                    <td style="text-align: center;">{f"{cantidad}"}</td>
                    <td class="right-align">{f"${float(precio_unitario):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")}</td>
                    <td class="right-align">{f"${float(total_linea):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")}</td>
                    </tr>"""
            detalle_html += f"""
                <tr>
                <td></td>
                <td colspan="3" class="table-active"><hr/></td>
                </tr>
                <td></td>
                <td colspan="2" class="table-active bold">Total :</td>
                <td class="bold right-align">${totalf}</td>
                </tr></tbody></table>
            """
            footer_html = f"""
                    <p></p>
                    <p></p>
                    <p class="bold">**Pago en Efectivo 13% de descuento</p>
                    <p><hr/></p>
                    <footer>{empresa.linea4}</footer>
                    <footer>{empresa.linea5}</footer>
                    <footer class="bold">ATENCION AL GREMIO CAMIONEROS</footer>
                    <footer class="bold">GRACIAS POR SEGUIRNOS!</footer>
                    </body></html>
                    """
                    #vaciar_carrito(request, id_empresa)
            ticket_html = cabecera_html + detalle_html + footer_html
                    # Si todo salió bien, devuelve una respuesta JSON de éxito
            return JsonResponse({'success': True, 'ticket_html': ticket_html})
        else:
            return JsonResponse({'success': False})

@login_required
def cerrar_venta(request, **kwargs):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
    if request.method == 'POST':
        id_empresa = kwargs['id_empresa']
        carrito = request.session.get(f'carrito_{id_empresa}', {})
        if carrito:

            empresa = get_object_or_404(empresas, id=id_empresa)

            carrito = request.session.get(f'carrito_{id_empresa}', {})
            data = json.loads(request.body)
            fpago = data.get('formapago', [])
            formapago = get_object_or_404(formaspago, id=fpago)
            descripcion_forma_pago = formapago.get_tipo_display()
            destoaeftvo = float(data.get('dtoefectivo', []))
            destoadicional = float(data.get('descuentoAdicional', []))
            subtotal = data.get('subtotal', [])
            total = data.get('total', [])
            cliente = data.get('cliente', [])
            tel_cliente = ''
            dir_cliente = ''
            try:
                cliente_obj = get_object_or_404(clientes, nombre=cliente, idempresa=id_empresa)
                cliente = cliente_obj.nombre + ' ' + cliente_obj.apellido
                tel_cliente = cliente_obj.telefono
                dir_cliente = cliente_obj.direccion + ' - ' + cliente_obj.ciudad + ' - ' + cliente_obj.provincia
            except:
                pass
            success = True
            if descripcion_forma_pago == 'Efectivo':
                dtoeftvo = destoaeftvo
            else:
                dtoeftvo = 0
            detalle_html = ''
            footer_html = ''
            try:
                # Inicia una transacción atómica
                with transaction.atomic():
                    # Crear la cabecera de la venta
                    cabecera = cabecera_venta.objects.create(empresa=empresa, fechav=timezone.now(),
                            cliente = cliente, formapago = formapago, subtotal = subtotal,
                            dtoeftvo = dtoeftvo, otrodto = destoadicional, imptotal=total)

                    tfechav = timezone.localtime(cabecera.fechav).strftime('%d-%m-%Y %H:%M:%S')
                    timp_dtoadi = subtotal * (destoadicional * 0.01 + 1) - subtotal
                    timp_dtoadif = f"{timp_dtoadi:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    if descripcion_forma_pago == 'Efectivo':
                        timp_dtoeft = subtotal * (float(empresa.dtoefectvo) * 0.01 + 1) - subtotal
                        timp_dtoeftf = f"{timp_dtoeft:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    else:
                        timp_dtoeftf = '0.00'

                    subtotalf = f"{subtotal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    totalf = f"{total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    cabecera_html = f"""
                    <html>
                    <head>
                        <title>Ticket</title>
                        <style>
                            body {{
                                font-family: Verdana, Geneva, sans-serif;
                                font-size: 10px;
                            }}
                            p{{
                                font-size: 10px;
                            }}
                            h3 {{
                                font-size: 12px;
                                font-weight: bold;
                            }}
                            .bold {{
                                font-weight: bold;
                            }}
                            .small {{
                                font-size: 10px;
                            }}
                            .xsmall {{
                                font-size: 6px;
                            }}
                            img {{
                                width: 200px;
                                height: 45px;
                                display: block;
                                margin: 0 auto; /* Centrará la imagen horizontalmente */
                            }}
                            subcab {{
                                font-sze : 6px;
                                width: 220px;
                                height: 6px;
                                display: block;
                                margin: 0 auto; /* Centrará la imagen horizontalmente */
                                text-align: center;
                            }}
                            footer {{
                                font-size : 8px;
                                width: 250px;
                                height: 10px;
                                display: block;
                                margin: 0 auto; /* Centrará la imagen horizontalmente */
                                text-align: center;
                            }}
                            table {{
                                width: 100%;
                                border-collapse: collapse;
                            }}
                            th, td {{
                                padding: 1px;
                                font-size: 8px;
                            }}
                            .left-align {{
                                text-align: left;
                            }}
                            .right-align {{
                                text-align: right;
                            }}
                            th {{
                                text-align: center; /* Centrar los encabezados por defecto */
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="row align-items-center">
                            <img src="{'/static/img/logo.png'}" alt="Logo">
                        </div>
                        <subcab class="xsmall">{empresa.linea1}</subcab>
                        <subcab class="xsmall">{empresa.linea2}</subcab>
                        <subcab class="small">{empresa.linea3}</subcab>
                        <p></p>
                        <hr/>
                        <p><span class="small bold">Nro.: </span>{cabecera.id}</p>
                        <p></p>
                        <p><span class="small bold">Fecha: </span>{tfechav}</p>
                        <hr/>
                        <p><span class="small bold">Cliente: </span>{cliente}</p>
                        <p><span class="small bold">Telefono: </span>{tel_cliente}</p>
                        <p><span class="small bold">Dirección: </span>{dir_cliente}</p>
                        <hr/>
                        <table>
                            <thead>
                                <tr>
                                    <th class="small">Artículo</th>
                                    <th class="small">Cant.</th>
                                    <th class="small">Precio</th>
                                    <th class="small">Subtotal</th>
                                </tr>
                            </thead>
                            <p></p>
                            <tbody>
                            <td colspan="4" class="table-active"><hr/></td>
                        """
                    # Iterar a través de las líneas y crearlas
                    for item in carrito.items():
                        #sum(item['cantidad'] for item in carrito.values())
                        articulo_id = item[0]
                        nombre_art = item[1]['nombre']
                        cantidad = f"{item[1]['cantidad']:.2f}"
                        precio_unitario = str(item[1]['precio'])
                        total_linea = str(item[1]['total_linea'])
                        # Recuperar el artículo
                        articulo = get_object_or_404(articulos, id=articulo_id)

                        # Calcula el subtotal para la línea
                        nuevo_stock = articulo.stock - Decimal(cantidad)

                        # Crear la línea de venta
                        hist_movart.objects.create(
                            empresa = empresa,
                            articulo = articulo,
                            fechamov = datetime.today(),
                            tipomov = 'Venta',
                            numdoc = cabecera.id,
                            cantidad = cantidad,
                            precioactual = Decimal(precio_unitario),
                            stockactual = articulo.stock,
                            nuevostock = Decimal(str(nuevo_stock)),
                            usuario = request.user,
                        )
                        articulo.stock = nuevo_stock
                        articulo.save()
                        detalle_html += f"""
                            <tr><td class="left-align">{nombre_art}</td>
                            <td style="text-align: center;">{f"{cantidad}"}</td>
                            <td class="right-align">{f"${float(precio_unitario):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")}</td>
                            <td class="right-align">{f"${float(total_linea):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")}</td>
                            </tr>"""
                detalle_html += f"""
                            <tr>
                            <td></td>
                            <td colspan="3" class="table-active"><hr/></td>
                            </tr>
                            <tr>
                            <td></td>
                            <td colspan="2" class="table-active bold">Subtotal :</td>
                            <td class="right-align bold">${subtotalf}</td>
                            </tr>
                            <tr>
                            <td></td>
                            <td colspan="2" class="table-active bold">Dto.:</td>
                            <td class="right-align bold">${timp_dtoadif}</td>
                            </tr>
                            <tr>
                            <td></td>
                            <td colspan="2" class="table-active bold">F. Pago :</td>
                            <td class="right-align bold">{descripcion_forma_pago}</td>
                            </tr>
                            <tr>
                            <td></td>
                            <td colspan="2" class="table-active bold">Dto. Efectivo : </td>
                            <td class="right-align bold">${timp_dtoeftf}</td>
                            </tr>
                            <tr>
                            <td></td>
                            <td colspan="2" class="table-active bold">Total :</td>
                            <td class="bold right-align">${totalf}</td>
                            </tr></tbody></table>
                    """
                footer_html = f"""
                <p></p>
                <p></p>
                <p><hr/></p>
                <p><hr/></p>
                <footer>{empresa.linea4}</footer>
                <footer>{empresa.linea5}</footer>
                <footer class="bold">ATENCION AL GREMIO CAMIONEROS</footer>
                <footer class="bold">GRACIAS POR SEGUIRNOS!</footer>
                </body></html>
                """
                vaciar_carrito(request, id_empresa)
                ticket_html = cabecera_html + detalle_html + footer_html
                # Si todo salió bien, devuelve una respuesta JSON de éxito
                return JsonResponse({'success': True, 'message': 'Venta registrada con éxito.', 'ticket_html': ticket_html})

            except Exception as e:
                # Si ocurre un error, la transacción se revierte automáticamente
                return JsonResponse({'success': False, 'message': str(e)})

        return JsonResponse({'success': False, 'message': 'Carrito está Vacío.'})

@login_required
def anular_venta(request, **kwargs):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    if request.method == 'POST':
        data = json.loads(request.body)
        nventa = data.get('id_venta', [])
                # Crear la cabecera de la venta
        cabecera = cabecera_venta.objects.get(id=nventa)
        empresa_id = cabecera.empresa
        cabecera.anulada= True
        cabecera.save()

        lineas = hist_movart.objects.filter(tipomov='venta', numdoc=nventa)

                # Iterar a través de las líneas y crearlas
        for item in lineas:
                    #sum(item['cantidad'] for item in carrito.values())
            articulo_id = item.articulo_id

            articulo = get_object_or_404(articulos, id=articulo_id)
            nuevo_stock = articulo.stock + item.cantidad
            hist_movart.objects.create(
                empresa = empresa_id,
                articulo = articulo,
                fechamov = datetime.today(),
                tipomov = 'Anula Venta',
                numdoc = nventa,
                cantidad = item.cantidad,
                precioactual = Decimal(item.precioactual),
                stockactual = articulo.stock,
                nuevostock = Decimal(str(nuevo_stock)),
                usuario = request.user,
                )
            articulo.stock = nuevo_stock
            articulo.save()
            # Si todo salió bien, devuelve una respuesta JSON de éxito
        return JsonResponse({'success': True, 'message': 'Venta Anulada con éxito.'})

@login_required
def reimprime_venta(request, **kwargs):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    if request.method == 'POST':
        data = json.loads(request.body)
        nventa = data.get('id_venta', [])
        empresa = data.get('idempresa')
        # Crear la cabecera de la venta
        cabecera = cabecera_venta.objects.get(id=nventa)
        empresa = empresas.objects.get(id=empresa)

        formapago = get_object_or_404(formaspago, id=cabecera.formapago.id)
        descripcion_forma_pago = formapago.get_tipo_display()

        nombre_cliente = ''
        telefono_cliente = ''
        direccion_cliente = ''
        if cabecera.cliente != '':
            try:
                cliente = clientes.objects.get(idempresa=empresa, nombre=cabecera.cliente)
                nombre_cliente = cliente.nombre + ' ' + cliente.apellido
                telefono_cliente = cliente.telefono
                direccion_cliente = cliente.direccion + ' - ' + cliente.ciudad + ' - ' + cliente.provincia
            except:
                pass

        tfechav = timezone.localtime(cabecera.fechav).strftime('%d-%m-%Y %H:%M:%S')
        timp_dtoadi = cabecera.subtotal * (cabecera.otrodto * Decimal(0.01)  + 1) - cabecera.subtotal
        timp_dtoadif = f"{timp_dtoadi:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        if cabecera.formapago.nombre == 'contado':
            timp_dtoeft = cabecera.subtotal * (empresa.dtoefectvo * Decimal(0.01) + 1) - cabecera.subtotal
            timp_dtoeftf = f"{timp_dtoeft:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            timp_dtoeftf = '0.00'

        subtotalf = f"{cabecera.subtotal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        totalf = f"{cabecera.imptotal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        cabecera_html = f"""
            <html>
            <head>
                <title>Ticket</title>
                <style>
                    body {{
                        font-family: Verdana, Geneva, sans-serif;
                        font-size: 10px;
                    }}
                    p{{
                        font-size: 10px;
                    }}
                    h3 {{
                        font-size: 12px;
                        font-weight: bold;
                    }}
                    .bold {{
                        font-weight: bold;
                    }}
                    .small {{
                    font-size: 10px;
                    }}
                    .xsmall {{
                        font-size: 6px;
                    }}
                    img {{
                        width: 200px;
                        height: 45px;
                        display: block;
                        margin: 0 auto; /* Centrará la imagen horizontalmente */
                    }}
                    subcab {{
                        font-sze : 6px;
                        width: 220px;
                        height: 6px;
                        display: block;
                        margin: 0 auto; /* Centrará la imagen horizontalmente */
                        text-align: center;
                    }}
                    footer {{
                        font-size : 8px;
                        width: 250px;
                        height: 10px;
                        display: block;
                        margin: 0 auto; /* Centrará la imagen horizontalmente */
                        text-align: center;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                    }}
                    th, td {{
                        padding: 1px;
                        font-size: 8px;
                    }}
                    .left-align {{
                    text-align: left;
                    }}
                    .right-align {{
                        text-align: right;
                    }}
                    th {{
                        text-align: center; /* Centrar los encabezados por defecto */
                    }}
                </style>
            </head>
            <body>
                <div class="row align-items-center">
                    <img src="{'/static/img/logo.png'}" alt="Logo">
                </div>
                <subcab class="xsmall">{empresa.linea1}</subcab>
                <subcab class="xsmall">{empresa.linea2}</subcab>
                <subcab class="small">{empresa.linea3}</subcab>
                <p></p>
                <hr/>
                <p><span class="small bold">Nro.: </span>{cabecera.id}</p>
                <p></p>
                <p><span class="small bold">Fecha: </span>{tfechav}</p>
                <hr/>
                <p><span class="small bold">Cliente: </span>{nombre_cliente}</p>
                <p><span class="small bold">Telefono: </span>{telefono_cliente}</p>
                <p><span class="small bold">Dirección: </span>{direccion_cliente}</p>
                <hr/>
                <table>
                    <thead>
                        <tr>
                            <th class="small">Artículo</th>
                            <th class="small">Cant.</th>
                            <th class="small">Precio</th>
                            <th class="small">Subtotal</th>
                        </tr>
                    </thead>
                    <p></p>
                    <tbody>
                    <td colspan="4" class="table-active"><hr/></td>
                """

        lineas = hist_movart.objects.filter(tipomov='venta', numdoc=nventa)

                # Iterar a través de las líneas y crearlas
        detalle_html = ''
        for item in lineas:
                    #sum(item['cantidad'] for item in carrito.values())

            nombre_art = item.articulo.descripcion
            cantidad = item.cantidad
            precio_unitario = str(item.precioactual)
            total_linea = str(item.cantidad * item.precioactual)
            # Recuperar el artículo
            detalle_html += f"""
                <tr><td class="left-align">{nombre_art}</td>
                <td style="text-align: center;">{f"{cantidad}"}</td>
                <td class="right-align">{f"${float(precio_unitario):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")}</td>
                <td class="right-align">{f"${float(total_linea):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")}</td>
                </tr>"""

        detalle_html += f"""
                <tr>
                <td></td>
                <td colspan="3" class="table-active"><hr/></td>
                </tr>
                <tr>
                <td></td>
                <td colspan="2" class="table-active bold">Subtotal :</td>
                <td class="right-align bold">${subtotalf}</td>
                </tr>
                <tr>
                <td></td>
                <td colspan="2" class="table-active bold">Dto.:</td>
                <td class="right-align bold">${timp_dtoadif}</td>
                </tr>
                <tr>
                <td></td>
                <td colspan="2" class="table-active bold">F. Pago :</td>
                <td class="right-align bold">{descripcion_forma_pago}</td>
                </tr>
                <tr>
                <td></td>
                <td colspan="2" class="table-active bold">Dto. Efectivo : </td>
                <td class="right-align bold">${timp_dtoeftf}</td>
                </tr>
                <tr>
                <td></td>
                <td colspan="2" class="table-active bold">Total :</td>
                <td class="bold right-align">${totalf}</td>
                </tr></tbody></table>
        """
        footer_html = f"""
                <p></p>
                <p></p>
                <p><hr/></p>
                <p><hr/></p>
                <footer>{empresa.linea4}</footer>
                <footer>{empresa.linea5}</footer>
                <footer class="bold">ATENCION AL GREMIO CAMIONEROS</footer>
                <footer class="bold">GRACIAS POR SEGUIRNOS!</footer>
                </body></html>
                """
        ticket_html = cabecera_html + detalle_html + footer_html

            # Si todo salió bien, devuelve una respuesta JSON de éxito
        return JsonResponse({'success': True, 'ticket_html': ticket_html})


@login_required
def movimientos_list_view(request, **kwargs):
    if not request.user.is_staff:
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    familia = request.GET['pfamilia']
    id_empresa = kwargs['id_empresa']
    empresas_var = empresas.objects.all()
    articulos_var = articulos.objects.filter(idempresa=id_empresa)
    familias_var = familias.objects.filter(idempresa=id_empresa)
    tipo_movs = [
        ('entrada', 'Compra'),
        ('entrada', 'Traspaso desde'),
        ('entrada', 'Anula Venta'),
        ('salida', 'Venta'),
        ('salida', 'Traspaso a'),
        ('regularizacion', 'Ajuste de stock'),
        ('crud', 'Creacion/actualizacion articulo'),
    ]

    # Renderizamos solo el HTML con la tabla vacía para que luego se llene vía AJAX
    return render(request, 'myapp/lista_movimientos.html', {
        'id_empresa': id_empresa,
        'empresas':empresas_var,
        'familias': familias_var,
        'articulos' : articulos_var,
        'tipo_movs' : tipo_movs,
        'fecha_desde': datetime.now().date(),
        'fecha_hasta': datetime.now().date(),
        'id_familia': familia
    })

@login_required
def ajax_list_movimientos(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    empresa = request.GET.get('empresa')
    articulo = request.GET.get('articulo')
    familia = request.GET.get('familia')
    tipomov = request.GET.get('tipomov')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    page_number = request.GET.get('page', 1)

    fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
    fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
    # convertir fecha_desde y fecha_hasta (datetime.date) a aware UTC
    fecha_desde_dt = datetime.combine(fecha_desde, time.min, tzinfo=dt_timezone.utc)
    fecha_hasta_dt = datetime.combine(fecha_hasta, time.max, tzinfo=dt_timezone.utc)

    # Aplicar los filtros al queryset
    if empresa == 'todos':
        movimientos = hist_movart.objects.filter(fechamov__range=(fecha_desde_dt, fecha_hasta_dt)).order_by('empresa','articulo', 'id')
    else:
        movimientos = hist_movart.objects.filter(empresa=empresa, fechamov__range=(fecha_desde_dt, fecha_hasta_dt)).order_by('empresa','articulo', 'id')

    if articulo != 'todos':
        movimientos = movimientos.filter(articulo=articulo)

    if familia != 'todos':
        movimientos = movimientos.filter(articulo__familia=familia)

    if tipomov != 'Todos':
        movimiento_filter = tipomov
        if tipomov == 'Creacion/actualizacion articulo':
            movimientos = movimientos.filter(Q(tipomov='Creacion Articulo') | Q(tipomov='Actualiza Articulo') | Q(tipomov='Actualizacion precio'))
        else:
            movimientos = movimientos.filter(tipomov=movimiento_filter)

    paginator = Paginator(movimientos, 10)  # 10 movimientos por página (ajústalo a tu preferencia)
    page_obj = paginator.get_page(page_number)

    movimientos_agrupados = {}
    for movimiento in page_obj.object_list:
        if movimiento.fechamov.hour == 0 and movimiento.fechamov.minute == 0 and movimiento.fechamov.second == 0:
            fecha_listado = movimiento.fechamov.strftime('%d-%m-%Y %H:%M:%S')
        else:
            fecha_listado = timezone.localtime(movimiento.fechamov).strftime('%d-%m-%Y %H:%M:%S')
        
        articulo = movimiento.articulo.descripcion
        if articulo not in movimientos_agrupados:
            movimientos_agrupados[articulo] = []
        movimientos_agrupados[articulo].append({
           # timezone.localtime(cabecera.fechav).strftime('%d-%m-%Y %H:%M:%S'),
            'fechamov': fecha_listado,
            'tipomov': movimiento.tipomov,
            'documento': movimiento.numdoc,  # Aquí agrego el número de documento que usas en el JS
            'cantidad': movimiento.cantidad,
            'stock': movimiento.stockactual,
            'nuevoprecio': movimiento.nuevoprecio,
            'nuevostock': movimiento.nuevostock,
            'usuario': movimiento.usuario.username,
        })

        # Serializar los resultados en JSON
    data = {
        'movimientos': movimientos_agrupados,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'page_number': page_obj.number,
        'total_pages': paginator.num_pages,
    }

    return JsonResponse(data)

@login_required
def ventas_list_view(request, **kwargs):
    if not request.user.is_staff:
        if not str(request.user.perfil.idempresa.id) == kwargs['id_empresa']:
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    familia = request.GET['pfamilia']
    id_empresa = kwargs['id_empresa']
    empresas_var = empresas.objects.all()

        # Renderizamos solo el HTML con la tabla vacía para que luego se llene vía AJAX
    return render(request, 'myapp/lista_ventas.html', {
        'id_empresa': id_empresa,
        'empresas':empresas_var,
        'fecha_desde': datetime.now().date(),
        'fecha_hasta': datetime.now().date(),
        'id_familia' : familia
    })


@login_required
def ajax_list_ventas(request):
    userstaff = True
    if not request.user.is_staff:
        userstaff = False
        if not str(request.user.perfil.idempresa.id) == request.GET.get('empresa'):
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    total_imptotal = 0
    empresa = request.GET.get('empresa')
    pfamilia = request.GET.get('pfamilia')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    page_number = request.GET.get('page', 1)

    fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
    fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
    # convertir fecha_desde y fecha_hasta (datetime.date) a aware UTC
    fecha_desde_dt = datetime.combine(fecha_desde, time.min, tzinfo=dt_timezone.utc)
    fecha_hasta_dt = datetime.combine(fecha_hasta, time.max, tzinfo=dt_timezone.utc)

    cabeceras_query = cabecera_venta.objects.filter(fechav__range=(fecha_desde_dt, fecha_hasta_dt))    
    if empresa != 'todos':
        empresa = int(empresa)
        cabeceras_query = cabeceras_query.filter(empresa_id=int(empresa))


    documentos_ids = cabeceras_query.values_list('id', flat=True)
    # Traer todos los movimientos de esas cabeceras (no solo 'venta')
    movimientos = hist_movart.objects.filter(
        numdoc__in=documentos_ids
    ).select_related('articulo', 'usuario')

    from collections import defaultdict

    movs_por_cab = defaultdict(list)
    usuario_anulo_por_cab = {}

    for m in movimientos:
        try:
            cab_id = int(m.numdoc)
        except (ValueError, TypeError):
            continue

        movs_por_cab[cab_id].append(m)

        # Guardar usuario que anuló
        if m.tipomov.lower() == 'anula venta':
            usuario_anulo_por_cab[cab_id] = m.usuario.username

    # Construir lista de ventas con movimientos
    ventas_con_movimientos = []
    total_imptotal = 0

    for cabecera in cabeceras_query:
        movis_cabecera = movs_por_cab.get(cabecera.id, [])
        if not movis_cabecera:
            continue

        dto_efectivo_importe = cabecera.subtotal * (cabecera.dtoeftvo / 100)
        otro_dto_importe = cabecera.subtotal * (cabecera.otrodto / 100)

        if cabecera.anulada:
            usuario_anulo = usuario_anulo_por_cab.get(cabecera.id, 'Desconocido')
            cab_anulada = f"Anulada por {usuario_anulo}"
        else:
            cab_anulada = ''
            total_imptotal += cabecera.imptotal

        ventas_con_movimientos.append({
            'cabecera': {
                'id': cabecera.id,
                'fechav': timezone.localtime(cabecera.fechav).strftime('%d-%m-%Y %H:%M:%S'),
                'cliente': cabecera.cliente,
                'fpago': cabecera.formapago.get_tipo_display(),
                'subtotal': format(cabecera.subtotal, ',.2f').replace(',', 'X').replace('.', ',').replace('X', '.'),
                'dtoeftvo': format(round(dto_efectivo_importe, 2), ',.2f').replace(',', 'X').replace('.', ',').replace('X', '.'),
                'otrodto': format(round(otro_dto_importe, 2), ',.2f').replace(',', 'X').replace('.', ',').replace('X', '.'),
                'imptotal': format(cabecera.imptotal, ',.2f').replace(',', 'X').replace('.', ',').replace('X', '.'),
                'usuario': movis_cabecera[0].usuario.username,
                'anulada': cab_anulada
            },
            'movimientos': [{
                'articulo': mov.articulo.descripcion,
                'cantidad': str(mov.cantidad),
                'precio': format(mov.precioactual, ',.2f').replace(',', 'X').replace('.', ',').replace('X', '.'),
            } for mov in movis_cabecera]
        })
    total_imptotal_formatted = format(round(total_imptotal, 2), ',.2f').replace(',', 'X').replace('.', ',').replace('X', '.')

    # Paginación
    paginator = Paginator(ventas_con_movimientos, 5)  # 5 resultados por página
    page_obj = paginator.get_page(page_number)

    data = {
        'ventas': page_obj.object_list,
        'total_imptotal': total_imptotal_formatted,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'num_pages': paginator.num_pages,
        'page_number': page_obj.number,
        'id_familia' : pfamilia,
        'userstaff' : userstaff
    }

    return JsonResponse(data)

'''@login_required
def ajax_list_ventas_produccio_sin_empresa(request):
    userstaff = True
    if not request.user.is_staff:
        userstaff = False
        if not str(request.user.perfil.idempresa.id) == request.GET.get('empresa'):
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    total_imptotal = 0
    empresa = request.GET.get('empresa')
    pfamilia = request.GET.get('pfamilia')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    page_number = request.GET.get('page', 1)

    fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
    fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
    if empresa == 'todos':
        movimientos = hist_movart.objects.filter(
            tipomov__icontains='venta',
            fechamov__range=(fecha_desde, fecha_hasta)
        ).order_by('articulo__idempresa')
    else:
        movimientos = hist_movart.objects.filter(
            articulo__idempresa=empresa,
            tipomov__icontains='venta',
            fechamov__range=(fecha_desde, fecha_hasta)
        ).order_by('articulo__idempresa')

    documentos_ids = movimientos.values_list('numdoc', flat=True).distinct()
    cabeceras_query = cabecera_venta.objects.filter(id__in=documentos_ids)
    # Filtrar los movimientos de tipo 'Venta'
    # Lista para almacenar los resultados
    ventas_con_movimientos = []

    for cabecera in cabeceras_query:
        dto_efectivo_importe = cabecera.subtotal * (cabecera.dtoeftvo / 100)
        otro_dto_importe = cabecera.subtotal * (cabecera.otrodto / 100)
        movis_cabecera = movimientos.filter(numdoc=cabecera.id)
        if movis_cabecera.exists():
            anula_venta = movis_cabecera.filter(tipomov='Anula Venta').first()
            if anula_venta:
                cab_anulada = 'Anulada por ' + anula_venta.usuario.username
            else:
                cab_anulada = ''
                total_imptotal += cabecera.imptotal
            ventas_con_movimientos.append({
                'cabecera': {
                    'id': cabecera.id,
                    'fechav': timezone.localtime(cabecera.fechav).strftime('%d-%m-%Y %H:%M:%S'),
                    'cliente': cabecera.cliente,
                    'fpago': cabecera.formapago.get_tipo_display(),  # Ejecuta el método
                    'subtotal': format(cabecera.subtotal, ',.2f').replace(',', 'X').replace('.', ',').replace('X', '.'),
                    'dtoeftvo': format(round(dto_efectivo_importe,2), ',.2f').replace(',', 'X').replace('.', ',').replace('X', '.'),
                    'otrodto': format(round(otro_dto_importe,2), ',.2f').replace(',', 'X').replace('.', ',').replace('X', '.'),
                    'imptotal': format(cabecera.imptotal, ',.2f').replace(',', 'X').replace('.', ',').replace('X', '.'),
                    'usuario': movis_cabecera[0].usuario.username,
                    'anulada' : cab_anulada
                },
                'movimientos': [{
                    'articulo': mov.articulo.descripcion,
                    'cantidad': str(mov.cantidad),
                    'precio': format(mov.precioactual, ',.2f').replace(',', 'X').replace('.', ',').replace('X', '.'),
                } for mov in movis_cabecera if mov.tipomov == 'Venta' or mov.tipomov == 'venta']
            })

    total_imptotal_formatted = format(round(total_imptotal, 2), ',.2f').replace(',', 'X').replace('.', ',').replace('X', '.')
        # Paginación
    paginator = Paginator(ventas_con_movimientos, 5)  # 10 resultados por página
    page_obj = paginator.get_page(page_number)

        # Preparar los datos para la respuesta en formato JSON
    data = {
        'ventas': page_obj.object_list,
        'total_imptotal': total_imptotal_formatted,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'num_pages': paginator.num_pages,
        'page_number': page_obj.number,
        'id_familia' : pfamilia,
        'userstaff' : userstaff
    }

    return JsonResponse(data)'''

@login_required
@user_passes_test(lambda u: u.is_superuser)
def backup_database(request):
    try:

        db_name = settings.DATABASES['default']['NAME']
        db_user = settings.DATABASES['default']['USER']
        db_password = settings.DATABASES['default']['PASSWORD']
        db_host = settings.DATABASES['default']['HOST'] or 'localhost'

        # Crear carpeta de backups si no existe
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        # Generar nombre del archivo con fecha y hora
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'backup_{db_name}_{timestamp}.sql')


        # Comando mysqldump EXCLUYENDO tablas del sistema
        dump_command = [
            'mysqldump',
            '--no-tablespaces',
            f'-h{db_host}',
            f'-u{db_user}',
            f'-p{db_password}',
            '--ignore-table=mysql.event',   # Ignorar tablas de sistema
            '--ignore-table=performance_schema.*',
            '--ignore-table=sys.*',
            '--ignore-table=information_schema.*',
            db_name
        ]

        # Ejecutar el dump
        with open(backup_file, 'w') as f:
            subprocess.run(dump_command, stdout=f, check=True)

        # Limpiar backups viejos: mantener solo los 7 más recientes
        backups = sorted(glob.glob(os.path.join(backup_dir, f'backup_{db_name}_*.sql')))
        if len(backups) > 7:
            for old_backup in backups[:-7]:
                os.remove(old_backup)

        return JsonResponse({'status': f'✅ Backup realizado: {os.path.basename(backup_file)}'})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'status': f'❌ Error en el dump: {str(e)}'})
    except Exception as e:
        return JsonResponse({'status': f'❌ Error general: {str(e)}'})

def catalogo_preview(request):
    # misma lógica que articulos_catalogo pero con template nuevo
    empresas_usuario = 2
    lista_familias = familias.objects.filter(idempresa=empresas_usuario)
    familias_con_imagen = []
    for familia in lista_familias:
        carpeta = familia.nombre
        cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME')
        imagen_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/dsilva/{carpeta}/generic.jpg"
        familias_con_imagen.append({'id': familia.id, 'nombre': familia.nombre, 'imagen': imagen_url})
    primera_familia = lista_familias.first()
    return render(request, 'catalogo/catalogo_new.html', {
        'familias': familias_con_imagen,
        'familia_actual': primera_familia,
    })

def articulos_catalogo(request):
    empresas_usuario = 2
    lista_familias = familias.objects.filter(idempresa=empresas_usuario)
    familias_con_imagen = []
    for familia in lista_familias:
        carpeta = familia.nombre
        cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME')
        imagen_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/dsilva/{carpeta}/generic.jpg"
        
        familias_con_imagen.append({
            'id': familia.id,
            'nombre': familia.nombre,
            'imagen': imagen_url
        })

    primera_familia = lista_familias.first()

    return render(request, 'catalogo/catalogo.html', {
        'familias': familias_con_imagen,
        'familia_actual': primera_familia,
        'articulos': articulos,
        'DEFAULT_IMAGE': static(settings.DEFAULT_IMAGE),
    })


def filtrar_articulos(request):
    familia_id = request.GET.get('familia_id')
    q = request.GET.get('q', '')
    page = request.GET.get('page', 1)

    articulos_filtrados = articulos.objects.filter(familia_id=familia_id, descripcion__icontains=q)
    paginator = Paginator(articulos_filtrados, 24)  # 12 artículos por página
    page_obj = paginator.get_page(page)

    html = render_to_string('catalogo/cards_articulos_new.html', {
        'articulos': page_obj, 'DEFAULT_IMAGE': static(settings.DEFAULT_IMAGE)
    })
    pagination_html = render_to_string("catalogo/pagination.html", {
        "page_obj": page_obj
    })


    return JsonResponse({'html': html, "pagination": pagination_html})

def articulo_detalle(request, pk):
    articulo = get_object_or_404(articulos, pk=pk)
    if articulo.stock <= 0:
        art_stock = 'Sin Stock'
    else:
        art_stock = "Disponible en Tienda"

    return render(request, 'catalogo/articulo_detalle.html', {
        'articulo': articulo,
        'art_stock': art_stock,
        'precio_schema': '{:.2f}'.format(articulo.precio_venta),  # ← NUEVO
        'DEFAULT_IMAGE': settings.DEFAULT_IMAGE,                  # ← NUEVO
    })


def catalogo_pdf(request):
    familia_id = request.GET.get('familia_id')
    if familia_id and familia_id != '0':
        familia = familias.objects.get(pk=familia_id)
        articulos_qs = articulos.objects.filter(familia=familia)
        titulo = f"Catálogo - {familia.nombre}"
    else:
        articulos_qs = articulos.objects.all()
        titulo = "Catálogo - Todas las familias"

    # Crear respuesta HTTP con tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="catalogo.pdf"'

    # Crear canvas
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, titulo)

    # Espaciado inicial
    y = height - 80
    p.setFont("Helvetica", 10)

    for art in articulos_qs:
        texto = f"{art.descripcion} - ${art.precio_venta}"
        p.drawString(50, y, texto)
        y -= 15

        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 10)
            y = height - 50

    p.save()
    return response