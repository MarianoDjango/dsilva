from .models import articulos, familias, empresas, clientes
#from django.forms import ModelForm, TextInput, Select, CheckboxInput
from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.utils import timezone
from datetime import date
import requests
from django.core.files.base import ContentFile

class articulosForm(forms.ModelForm):
    #imagen_file = forms.ImageField(required=False)

    precio_venta = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'text-align: right;', 'readonly': 'readonly'})
    )
    fecha_precio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'style': 'text-align: right;', 'readonly': 'readonly'}, format='%Y-%m-%d'),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        initial= now().date()
    )
    stock = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'text-align: right;', 'readonly': 'readonly'})
    )
    fecha_stock = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'style': 'text-align: right;', 'readonly': 'readonly'}, format='%Y-%m-%d'),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        initial= now().date()
    )

    class Meta:
        model = articulos
        fields = ['idempresa', 'codigobarras', 'familia', 'descripcion', 'precio_venta', 
                  'fecha_precio', 'stock', 'fecha_stock', 'imagen', 'activo', 
                  'comentarios', 'precio_compra', 'margen', 'margen2', 'descripcion_seo']
        widgets = {
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'familia': forms.Select(attrs={'class': 'form-select'}),  # Si familia se ve como input, prueba con Select
            'fecha_precio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_stock': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'style': 'text-align: right;'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'style': 'text-align: right;'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control', 'style': 'text-align: right;'}),
            'margen': forms.NumberInput(attrs={'class': 'form-control', 'style': 'text-align: right;'}),
            'margen2': forms.NumberInput(attrs={'class': 'form-control', 'style': 'text-align: right;'}),
            'descripcion_seo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        empresa_id = kwargs.pop('empresa_id', None)
        super(articulosForm, self).__init__(*args, **kwargs)
        
        if empresa_id:
            try:
                self.fields['familia'].queryset = familias.objects.filter(idempresa=empresa_id).order_by('nombre')
            except (ValueError, TypeError):
                self.fields['familia'].queryset = familias.objects.none()
        elif self.instance.pk:
            self.fields['familia'].queryset = self.instance.idempresa.familias_set.order_by('nombre')
        
        if self.instance.pk:
            self.fields['fecha_precio'].initial = self.instance.fecha_precio
            self.fields['fecha_stock'].initial = self.instance.fecha_stock
        else:
            self.fields['fecha_precio'].initial = timezone.now().date()
            self.fields['fecha_stock'].initial = timezone.now().date()

        # Asegúrate de que todos los campos tengan la clase form-control
        for field in self.fields:
            if not isinstance(self.fields[field].widget, forms.CheckboxInput):
                self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['familia'].label_from_instance = lambda obj: obj.nombre                
    
    '''def clean(self):
        cleaned_data = super().clean()
        imagen_archivo = cleaned_data.get("imagen_cloud")
        imagen_url = cleaned_data.get("imagen_url")

        if not imagen_archivo and not imagen_url:
            raise ValidationError("Debe seleccionar una imagen o proporcionar una URL.")

        if not imagen_archivo and imagen_url:
            try:
                response = requests.get(imagen_url)
                response.raise_for_status()
                nombre = imagen_url.split("/")[-1]
                contenido = ContentFile(response.content)
                self._imagen_descargada = (nombre, contenido)
            except Exception:
                raise ValidationError("No se pudo descargar la imagen desde la URL.")

        return cleaned_data'''

class clientesForm(forms.ModelForm):

    class Meta:
        model = clientes
        fields = ['idempresa', 'nombre', 'apellido', 'email', 'telefono', 
                  'direccion', 'ciudad', 'provincia', 'codigo_postal', 
                  'activo']
        widgets = {
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        empresa_id = kwargs.pop('empresa_id', None)
        super(clientesForm, self).__init__(*args, **kwargs)

        # Asegúrate de que todos los campos tengan la clase form-control
        for field in self.fields:
            if not isinstance(self.fields[field].widget, forms.CheckboxInput):
                self.fields[field].widget.attrs.update({'class': 'form-control'})
        # Hacer que el email no sea obligatorio en el formulario
        self.fields['email'].required = False

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:  # Solo hacer validación si el email no está vacío
            if clientes.objects.filter(email=email).exists():
                raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email
'''class MovimientosFiltroForm(forms.Form):
    empresa = forms.ModelChoiceField(
        queryset=empresas.objects.all(), required=False, label='Empresa')
    articulo = forms.ModelChoiceField(
        queryset=articulos.objects.all(), required=False, label="Artículo", empty_label="Todos"
    )
    familia = forms.ModelChoiceField(
        queryset=familias.objects.all(), required=False, label="Familia", empty_label="Todas"
    )
    tipomov = forms.ChoiceField(
        choices=[
            ('todos', 'Todos'),
            ('compra', 'Compra'),
            ('traspaso', 'Traspaso'),
            ('venta', 'Venta'),
            ('ajuste', 'Ajuste Stock'),
            ('crud', 'Creacion/Actualizacion'),
        ],
        required=False, label="Tipo Movimiento"
    )
    fecha_desde = forms.DateField(
        required=False, label="Fecha Desde",
        widget=forms.TextInput(attrs={'type': 'date'}),
        initial=date.today
    )
    fecha_hasta = forms.DateField(
        required=False, label="Fecha Hasta",
        widget=forms.TextInput(attrs={'type': 'date'}),
        initial=date.today
    )

    def __init__(self, *args, **kwargs):
        empresa_seleccionada = kwargs.pop('empresa', None)
        super(MovimientosFiltroForm, self).__init__(*args, **kwargs)

        # Filtrar los artículos según la empresa seleccionada
        if empresa_seleccionada:
            self.fields['articulo'].queryset = articulos.objects.filter(idempresa=empresa_seleccionada)
        else:
            self.fields['articulo'].queryset = articulos.objects.all()

        # Añadir la opción 'Todos' a los selects
        self.fields['articulo'].choices = [('todos', 'Todos')] + list(self.fields['articulo'].choices)
        self.fields['familia'].choices = [('todos', 'Todos')] + list(self.fields['familia'].choices)
'''