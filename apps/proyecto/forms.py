# === Importamos las librerias necesarias para la implementación de un Formulario ===
from django import forms
from .models import Proyecto
from django.db.models import Q
from apps.usuario.models import User

# === Clase para abstraer en un formulario el registro de un Proyecto ===<br/>
from ..fase.models import Fase


class FormularioProyecto(forms.ModelForm):
    # Clase que modela el formulario de la definición de un proyecto a ser usado en la plantilla </br>
    # Para read - only los fields estado y fecha_creacion<br/>

    def __init__(self, *args, **kwargs):
        """
        Constructor de la clase para configurar los campos a restringir evitando asi su modificación y que solo<br/>
        este disponible para visualizar <br/>
        **:param args:**
        **:param kwargs:** Un diccionario del formulario de registro del proyecto<br/>
        """
        user_gerente = kwargs.pop('gerente') #se obtiene el username del gerente, que será excluido de los posibles miembros de su proyecto
        super(FormularioProyecto, self).__init__(*args, **kwargs)
        
        self.fields['miembros'].required = True
        self.fields['miembros'].disabled = False

        self.fields['miembros'].queryset = User.objects.filter(~Q(is_superuser=True) & ~Q(is_active=False)).exclude(username='AnonymousUser').exclude(username=user_gerente).exclude(username='adminsgcas07')
        # queryset que excluye al AnonymousUser  y al superusuario del sistema, de los posibles miembros del proyecto.

        campos = ['fecha_creacion', 'estado']

        for field in campos:
            self.fields[field].required = False
            self.fields[field].disabled = True

    class Meta:
        # **Clase Meta que tiene como función definir el formulario que va se desplegado en la plantilla**<br/>
        model = Proyecto
        fields = [
            'nombre',
            'descripcion',
            'miembros',
            'fecha_creacion',
            'estado',

        ]

        # Las etiquetas que tendrá para visualizarse en el navegador<br/>
        labels = {
            'nombre': 'Nombre del Proyecto',
            'descripcion': 'Descripción del Proyecto',
            'miembros': 'Miembros',
            'fecha_creacion': 'Fecha de Creación',
            'estado': 'Estado actual',
        }
        # los aparatos o elementos de captura de información del formulario<br/>
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control',
                                             'placeholder': 'Introduzca el nombre del proyecto'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control',
                                                 'placeholder': 'Agregue una descripción al proyecto'}),
            'miembros': forms.CheckboxSelectMultiple(),
            'fecha_creacion': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
        }


class FormularioProyectoUpdate(FormularioProyecto):
    # **Clase que modela el formulario de la definición de un proyecto a ser usado en la plantilla**<br/>

    # Para read - only los fields que se presentan en la siguiente lista.<br/>
    def __init__(self, *args, **kwargs):               
        super(FormularioProyectoUpdate, self).__init__(*args, **kwargs)
        
        user_gerente = kwargs.pop('gerente')
        
        self.fields['miembros'].required = True
        self.fields['miembros'].disabled = False

        self.fields['miembros'].queryset = User.objects.filter(~Q(is_superuser=True) & ~Q(is_active=False)).exclude(username='AnonymousUser').exclude(username=user_gerente).exclude(username='adminsgcas07')
        # fields representa los campos que no son editables de acuerdo al estado del proyecto<br/>
        fields = ['nombre', 'fecha_creacion', 'estado']
        if 'instance' in kwargs:
            # No se permite la modificacion del nombre del proyecto si su estado es pendiente<br/>
            # if kwargs['instance'].estado == 'Pendiente' or kwargs['instance'].estado == 'Iniciado' or \<br/>
            # kwargs['instance'].estado == 'Finalizado' or kwargs['instance'].estado == 'Cancelado':<br/>
            for field in fields:
                self.fields[field].required = False
                self.fields[field].disabled = True

    class Meta(FormularioProyecto.Meta):
        model = Proyecto


class ChangeProject(forms.ModelForm):
    # Clase para actualizar los cambios de estado de un proyecto , ese cambio se hace por medio de un formulario.
    def __init__(self, *args, **kwargs):
        """
        Constructor de la clase para obtener el diccionario de los datos de la instancia del formulario de un proyecto<br/>
        **:param args:** <br/>
        **:param kwargs:** recibe el diccionario con los datos del proyecto <br/>
        """
        super(ChangeProject, self).__init__(*args, **kwargs)
        # fields representa los campos que no son editables de acuerdo al estado del proyecto
        fields = ['nombre', 'descripcion', 'fecha_creacion', 'miembros']
        # No se permite la modificacion del nombre del proyecto si su estado es pendiente
        gerente = kwargs['instance'].gerente

        cerrado = True      # Cerrado valida que todas las fases esten cerradas para finalizar un proyecto, asumo entonces que inicialmente todas las fases estan cerradas
        for fase in Fase.objects.filter(proyecto=kwargs['instance']):   # y en este for lo que hago es, si encuentra al menos 1 fase abierta entonces no se puede finalizar el proyecto
            if fase.estado == 'Abierta':
                cerrado = False

        if Fase.objects.filter(proyecto=kwargs['instance']) and kwargs['instance'].estado == "Pendiente":
        # if kwargs['instance'].estado == 'Pendiente':
            estado_proyecto = [
                ('Pendiente', 'Pendiente'),
                ('Iniciado', 'Iniciado'),
            ]
            self.fields['estado'].choices = estado_proyecto

        elif kwargs['instance'].estado == 'Iniciado' and cerrado:       # Cerrado valida que todas las fases esten cerradas para finalizar un proyecto
            estado_proyecto = [
                ('Iniciado', 'Iniciado'),
                ('Cancelado', 'Cancelado'),
                ('Finalizado', 'Finalizado'),
            ]
            self.fields['estado'].choices = estado_proyecto
        elif kwargs['instance'].estado == 'Iniciado':
            estado_proyecto = [
                ('Iniciado', 'Iniciado'),
                ('Cancelado', 'Cancelado'),
            ]
            self.fields['estado'].choices = estado_proyecto
        elif kwargs['instance'].estado == 'Pendiente':
            estado_proyecto = [
                ('Pendiente', 'Pendiente'),
            ]
            self.fields['estado'].choices = estado_proyecto

        for field in fields:
            self.fields[field].required = False
            self.fields[field].disabled = True

    class Meta:
        # **Campos a ser filtrados en la plantilla del formulario**
        model = Proyecto
        fields = [
            'nombre',
            'descripcion',
            'miembros',
            'fecha_creacion',
            'estado',

        ]
        # **Las etiquetas a ser visualizadas**
        labels = {
            'estado': 'Cambiar de estado',
        }
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

# **Volver atras** : [[apps.py]]

# **Ir a la documentación del modelo de la Aplicación** :[[models.py]]

# === Indice de la documentación de la Aplicación Proyecto  === <br/>
# 1.admin   : [[admin.py]]<br/>
# 2.apps    : [[apps.py]]<br/>
# 3.forms   : [[forms.py]]<br/>
# 4.models  : [[models.py]]<br/>
# 5.tests   : [[tests.py]]<br/>
# 6.urls    : [[urls.py]]<br/>
# 7.views   : [[views.py]]<br/>

# Regresar al menu principal : [Menú Principal](../../docs-index/index.html)
