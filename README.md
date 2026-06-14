# 🛒 Sistema de Gestión Comercial + Catálogo Web (Django)

Aplicación web desarrollada con **Django y Django REST Framework** para la gestión integral de una distribuidora de artículos de gomería.

El sistema combina una **landing pública con catálogo de productos** y un **panel interno de gestión**, permitiendo centralizar operaciones comerciales y mejorar la atención al cliente.

---

## 🌐 Demo en producción

👉 https://www.silvadistribuidora.com/

> Aplicación actualmente en uso real.

---

## 🚀 Funcionalidades principales

### 🌐 Frontend / Landing
- Catálogo de productos con imágenes
- Navegación por categorías
- Visualización optimizada para clientes
- Enlace directo a WhatsApp para consultas rápidas

### 🔐 Panel de gestión (backend)
- Gestión completa de artículos con imágenes
- Control de stock en tiempo real
- Movimientos de stock manuales
- Registro y gestión de ventas
- Generación e impresión de presupuestos
- Administración de datos comerciales

### 🔄 API REST (Django REST Framework)
- Endpoints para consultas asincrónicas
- Integración frontend-backend
- Manejo eficiente de datos

---

## 🧠 Arquitectura del sistema

El proyecto está dividido en tres componentes principales:

- **Frontend:** Django Templates + Bootstrap orientado a experiencia de usuario
- **Backend:** Panel de gestión con lógica de negocio (stock, ventas, productos)
- **API REST:** Implementada con DRF para consultas asincrónicas y desacople

---

## 💼 Casos de uso reales

- Clientes consultan productos desde el catálogo y contactan vía WhatsApp
- El administrador gestiona stock y productos en tiempo real
- Generación de presupuestos para ventas directas
- Control manual de movimientos de inventario

---

## 🎯 Valor aportado

- Digitalización de un negocio tradicional
- Mejora en la captación de clientes online
- Centralización de la gestión comercial
- Reducción de errores en el control de stock

---

## 🛠 Tecnologías utilizadas

- **Backend:** Python, Django, Django REST Framework  
- **Frontend:** HTML, CSS, Bootstrap  
- **Base de datos:** MySQL  
- **Otros:** Cloudinary, integración con WhatsApp  

---

## 🧩 Features técnicas

- ORM de Django para gestión de datos
- Relaciones entre modelos (ForeignKey)
- Manejo de imágenes con Cloudinary
- Vistas basadas en funciones
- Consumo de API REST con JavaScript (consultas asincrónicas)

---

## 📸 Capturas

- Catálogo público
- Panel de administración
- Vista de productos
- Generación de presupuestos

---

## ⚙️ Instalación (modo desarrollo)

```bash
git clone https://github.com/MarianoDjango/sistema-distribuidora-django.git
cd sistema-distribuidora-django

python -m venv venv
source venv/bin/activate  # o venv\\Scripts\\activate en Windows

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver


## 👨‍💻 Autor

**Mariano Scaglia**  
Backend Developer especializado en Django y desarrollo de sistemas comerciales.

- 💼 LinkedIn: https://www.linkedin.com/in/mariano-scaglia-25067628/
- 💻 GitHub: https://github.com/MarianoDjango
