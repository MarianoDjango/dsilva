from cloudinary.models import CloudinaryField
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import locale

class formaspago(models.Model):
    FORMASP_CHOICES = [
        ('credito', 'Tarjeta Credito'), #sst codigo que indica que se SUMA al stock lo entrado por sistema
        ('debito', 'Tarjeta Debito'), #rst codigo que indica que se le debe RESTA al stock lo entrado por sistema
        ('contado', 'Efectivo'), #ast codigo que indica que se ACTUALIZA el stock a lo entrado por sistema
        ('transferencia', 'Transferencia/QR')  
    ]
    
    APLICA_DTO = ['contado']
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=FORMASP_CHOICES)
    aplicadto = models.BooleanField(default=0) #indica si la forma de pago aplica dto 0=False, 1=True
    aplicargo = models.BooleanField(default=0) #indica si forma de pago aplica recargo 0=False, 1=True

    def save(self, *args, **kwargs):
        # Determina si aplica descuento o recargo basado en `tipo`
        self.aplicadto = self.tipo in self.APLICA_DTO
        self.aplicargo = self.tipo in self.APLICA_DTO
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

class tipomovimientos(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('regularizacion', 'Regularización'),
    ]

    MOTIVO_CHOICES = [
        ('compra', 'Compra'),  # Entrada
        ('traspaso_entrada', 'Traspaso desde'),  # Entrada
        ('venta', 'Venta'),  # Salida
        ('traspaso_salida', 'Traspaso a'),  # Salida
        ('ajuste', 'Ajuste de stock'),  # Regularización
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    motivo = models.CharField(max_length=30, choices=MOTIVO_CHOICES, default=None)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_motivo_display()}"
    
class empresas(models.Model):
    name = models.CharField(max_length=255,blank=False, null=False)
    dtoefectvo = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)   # Porcentaje de descuento por pago en efectivo
    margen_emp = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Porcentaje de margen
    recargo_emp = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Porcentaje de recargo pago tarjeta
    venta = models.BooleanField(default=True)
    linea1 = models.CharField(max_length=100, blank=True, null=True, default=None)
    linea2 = models.CharField(max_length=100, blank=True, null=True, default=None)
    linea3 = models.CharField(max_length=100, blank=True, null=True, default=None)
    linea4 = models.CharField(max_length=100, blank=True, null=True, default=None)
    linea5 = models.CharField(max_length=100, blank=True, null=True, default=None)
    imagenes = models.BooleanField(default=False)  # Indica si se usan imagenes en articulos

    def __str__(self):
        return f"{self.id} - {self.name}"

class perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50, null=True, default=None)
    idempresa = models.ForeignKey(empresas, on_delete=models.CASCADE, null=True)
    
    def __str__(self): 
        return str(self.user)
    class Meta:
        ordering = ["nombre"]
    
class familias(models.Model):
    idempresa = models.ForeignKey(empresas, on_delete=models.CASCADE, null=True)
    nombre = models.CharField(max_length = 50, blank=True, null=True)

    def __str__(self):
        return str(self.id) + "-" + self.nombre

    class Meta:
        ordering = ["id"]
        verbose_name = "Familias"    


class articulos(models.Model):
    idempresa = models.ForeignKey(empresas, on_delete=models.CASCADE, null=True)
    codigobarras = models.CharField(max_length = 15, blank=False, null=False, default=0)
    familia = models.ForeignKey(familias, on_delete=models.CASCADE, null=True)
    descripcion = models.CharField(max_length = 200, blank=False, null=False)
    precio_venta = models.DecimalField(max_digits =  11, decimal_places = 2, default=0)
    fecha_precio = models.DateField()
    stock = models.DecimalField(max_digits =  7, decimal_places = 2, default=0)
    fecha_stock = models.DateField()
    imagen = models.CharField(max_length = 250, blank=True)
    activo = models.BooleanField(default=True)
    comentarios = models.CharField(max_length = 250, blank=True)
    precio_compra = models.DecimalField(max_digits =  11, decimal_places = 2, default=0)
    margen = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Porcentaje de margen
    margen2 = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Porcentaje de margen
    imagen_cloud = CloudinaryField('imagen', blank=True, null=True)
    descripcion_seo = models.TextField(blank=True, null=True)

    @property
    def precio_venta_formateado(self):
        try:
            return locale.currency(self.precio_venta, grouping=True, symbol=True)
        except Exception:
            return f"$ {self.precio_venta:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
            
    @property
    def imagen_cloud_url(self):
        if self.imagen_cloud:
            return self.imagen_cloud.url
        return None
    
    def __str__(self):
        return self.descripcion

    def get_absolute_url(self):
        return reverse("article-detail", kwargs={"pk": self.pk})
    
    class Meta:
        ordering = ["-activo","familia", "descripcion"]

class clientes(models.Model):
    idempresa = models.ForeignKey(empresas, on_delete=models.CASCADE, null=True) 
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True)
    email = models.CharField(unique=True, max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class cabecera_venta(models.Model):
    empresa = models.ForeignKey('empresas', on_delete=models.CASCADE, 
        null=True,  # temporalmente null para migración
        blank=True
    )
    fechav = models.DateTimeField()    
    cliente = models.CharField(max_length = 50, default='') #este campo permite entrar un nombre cuando elcliente es el 0='generico'
    formapago = models.ForeignKey(formaspago, on_delete=models.CASCADE, null=False)
    subtotal = models.DecimalField(max_digits=13, decimal_places=2, default=0.00)
    dtoeftvo = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    otrodto = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    recargo = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    imptotal = models.DecimalField(max_digits=13, decimal_places=2, default=0.00)
    anulada = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.id} - {self.cliente} - {self.empresa}"    
    
class hist_movart(models.Model):
    empresa = models.ForeignKey('empresas', on_delete=models.CASCADE, 
        null=True,  # temporalmente null para migración
        blank=True
    )
    articulo = models.ForeignKey(articulos, on_delete=models.CASCADE, null=False)
    fechamov = models.DateTimeField(null=True, blank=True)  # temporalmente null para migración
    tipomov = models.CharField(max_length=20, null=False)
    numdoc = models.CharField(max_length = 50, default=0) #este campo representa numero tique venta o numero de remito o factura de compra o nombre de empresa en caso de traspasos
    cantidad = models.DecimalField(max_digits =  7, decimal_places = 2, default=0.00)
    precioactual = models.DecimalField(max_digits =  11, decimal_places = 2, default=0) 
    porprecio = models.DecimalField(max_digits=5, decimal_places=2, default=0.00) #porcentaje de suba o baja de precio
    nuevoprecio = models.DecimalField(max_digits =  11, decimal_places = 2, default=0.00)
    stockactual = models.DecimalField(max_digits =  7, decimal_places = 2, default=0.00)
    nuevostock = models.DecimalField(max_digits =  7, decimal_places = 2, default=0)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
# Create your models here.


