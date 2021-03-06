from django.contrib.auth.mixins import LoginRequiredMixin
from guardian.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required

from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
# **Importamos los codigos fuentes de la aplicación para la creación de vistas
from SGCAS.decorators import requiere_permiso
from .models import Proyecto
from apps.fase.models import Fase
from apps.usuario.models import User

from django.db.models import Q
from django.core.paginator import Paginator
from .forms import FormularioProyecto, FormularioProyectoUpdate, ChangeProject
import datetime

from ..item.models import Item
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

"""
Todas las vistas para la aplicación del Modulo Proyecto

Actualmente se despliega en las plantillas 9 vistas:

1. **manage_projects** - vista que despliega gestión de proyectos (Ir a la sección: [[views.py #manage_projects]] )<br/>
2. **success** - vista que despliega la operación exitosa de la definición de un proyecto (Ir a la sección: [[views.py #success]] )<br/>
3. **change_state** - vista que despliega el cambio de estado de un proyecto (Ir a la sección: [[views.py #change_state]] )<br/>
4. **CreateProject** - vista que despliega el formulario para definición de proyectos (Ir a la sección: [[views.py #create project]] )<br/>
5. **ListProject** - vista que despliega el listado de proyectos (Ir a la sección: [[views.py #list project]] )<br/>
6. **search** - vista que despliega una lista de proyectos buscados (Ir a la sección: [[views.py #search]] )<br/>
7. **UpdateProject** - vista que despliega la opción de actualizar un proyecto (Ir a la sección: [[views.py #update project]] )<br/>
8. **DeleteProject** - vista que despliega el borrado de un proyecto (Ir a la sección: [[views.py #delete project]] )<br/>
9. **DetailProject** - vista que despliega los detalles referentes a un proyecto (Ir a la sección: [[views.py #detail project]] )<br/>

"""


@login_required
@permission_required('proyecto.gestion_proyecto', raise_exception=True)
# === manage_projects ===
def manage_projects(request):
    """
    Recibe una petición a la pagina de proyecto por parte de un cliente, esta vista basada en una función retorna
    la pagina principal para la gestión de proyectos.<br/>
    **:param:** request<br/>
    **:return:** retorna la plantilla de gestión de proyectos<br/>
    """
    return render(request, 'proyecto/manage_projects.html')


@login_required
# === success ===
def success(request):
    """
    Una vista basada en función donde indica la creación exitosa de una operacion sobre proyectos.<br/>
    **:param request:** recibe la petición del cliente.<br/>
    **:return:** plantilla mostrando la operación exitosa.<br/>
    """
    return render(request, 'proyecto/success.html')


@login_required
@permission_required('proyecto.cambiar_estado', raise_exception=True)
# === change_state ===
def change_state(request, pk):
    """

    Vista basada en función donde desplegamos en una plantilla las diferentes transaciónes que pasa un proyecto.<br/>
    para el registro de sus cambios de estado.<br/>
    **:param request:** Solicitud del cliente para el cambio de estado.<br/>
    **:param pk:** Recibe la instancia del modelo proyecto a ser cambiado.<br/>
    **:return:** Realiza el cambio de estado , guarda en la base de datos y retorna el proyecto con su nuevo estado.<br/>
    """
    proyecto = get_object_or_404(Proyecto, id=pk)
    form = ChangeProject(request.POST or None, instance=proyecto)
    if proyecto.gerente == request.user:
        if form.is_valid():
            if proyecto.estado == 'Iniciado':
                proyecto.fecha_iniciado = datetime.date.today()
            elif proyecto.estado == 'Cancelado':
                proyecto.fecha_cancelado = datetime.date.today()
            elif proyecto.estado == 'Finalizado':
                proyecto.fecha_finalizado = datetime.date.today()
            proyecto.save()
            form.save()
            return redirect('proyecto:list')
        return render(request, 'proyecto/change.html', {'form': form, 'proyecto': proyecto})
    else:
        return render(request, 'proyecto/validate_estado_transicion.html')


# === create project ===
class CreateProject(CreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """
    Permite la visualizacion en una plantilla para la definición de un proyecto.<br/>
    **:param PermissionRequiredMixin:** Libreria que gestiona el permiso para la creación de proyectos.El usuario
    debe poseer el permiso correspondiente de crear proyectos.<br/>
    **:param LoginRequiredMixin:** Requiere que el usuario este logueado en el sistema.<br/>
    **:param CreateView:** Recibe una vista generica de tipo CreateView para vistas basadas en clases.<br/>
    **:return:** Crea una instancia del modelo proyecto y lo guarda en la base de datos.<br/>
    """
    model = Proyecto
    form_class = FormularioProyecto
    permission_required = 'proyecto.crear_proyecto'
    template_name = 'proyecto/create.html'
    success_url = reverse_lazy('proyecto:success')

    # def get(self, request, **kwargs):
    #     ##revisar si existen usuarios en el sistema.
    #     ##si no existen, redirigir a un template que diga que no existen usuarios en el sistema
    #     ## si existen llamar get_form_kwargs(self, **kwargs)
        

    def get_form_kwargs(self, **kwargs):
        kwargs = super(CreateProject, self).get_form_kwargs(**kwargs)
        kwargs['gerente'] = self.request.user  # se envia al formulario el username del gerente
        return kwargs

    def form_valid(self, form):
        """
        Función de validación de los registros de un formulario y ademas guarda los datos que se obtuvieron en los cambpos en la base de datos<br/>
        **:param form:** recibe el formulario form<br/>
        **:return:** guarda los datos en la base de datos y redirige a una plantilla de Operación exitosa<br/>
        """
        self.object = form.save(commit=False)

        self.object.gerente = self.request.user  # intuimos que el creador del proyecto va ser el gerente

        self.object.save()
        form.save_m2m()  # Para guardar as relaciones manytomany
        return HttpResponseRedirect(self.get_success_url())


# === list project ===
class ListProject(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    """
    Permite la visualizacion de los proyectos.<br/>
    **:param PermissionRequiredMixin:** Libreria que gestiona el permiso para la creación de proyectos.El usuario
    debe poseer el permiso correspondiente de visualizar proyectos.<br/>
    **:param LoginRequiredMixin:** Requiere estar logueado, de la libreria django.contrib.auth.mixins<br/>
    **:param ListView:** Recibe una vista generica de tipo ListView para vistas basadas en clases.<br/>
    **:return:** Una vista de todos los proyectos.<br/>
    """

    paginate_by = 4
    model = Proyecto
    permission_required = 'proyecto.ver_proyecto'
    template_name = 'proyecto/list.html'

    def get_queryset(self):
        # Queryset que muestra los proyectos del que el usuario forma parte
        return Proyecto.objects.filter(Q(gerente=self.request.user) | Q(miembros=self.request.user)).order_by(
            'id').distinct()


@permission_required('proyecto.ver_proyecto', raise_exception=True)
# === search ===
def search(request):
    """
    Permite la búsqueda de los proyectos.<br/>
    **:param request:** Recibe un request por parte de un usuario.<br/>
    **:return:** retorna una lista con los proyectos que cumplan con los criterios de búsqueda.<br/>
    """
    template = 'proyecto/list_busqueda.html'
    query = request.GET.get('buscar')

    if query:
        results = Proyecto.objects.filter((Q(gerente=request.user) | Q(miembros=request.user)) &
                                          (Q(nombre__icontains=query) | Q(descripcion__contains=query))).order_by(
            'id').distinct()
    else:
        results = Proyecto.objects.filter(Q(gerente=request.user) | Q(miembros=request.user)).order_by('id').distinct()

    paginator = Paginator(results, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, template, {'page_obj': page_obj})


# === update project ===
class UpdateProject(LoginRequiredMixin, UpdateView, PermissionRequiredMixin):
    """
    Permite la actualizacion una instancia de modelo Proyecto.<br/>
    **:param PermissionRequiredMixin:** Libreria que gestiona el permiso para la creación de proyectos.El usuario
    debe poseer el permiso correspondiente de modificación de proyectos.<br/>
    **:param LoginRequiredMixin:** Requiere estar logueado, de la libreria django.contrib.auth.mixins<br/>
    **:param UpdateView:** Recibe una vista generica de tipo UpdateView para vistas basadas en clases.<br/>
    **:return:** Actualiza una instancia del modelo Proyecto, luego se redirige a la lista de proyectos.<br/>
    """
    model = Proyecto
    template_name = 'proyecto/update.html'
    form_class = FormularioProyectoUpdate
    permission_required = 'proyecto.editar_proyecto'

    def get_form_kwargs(self, **kwargs):
        kwargs = super(UpdateProject, self).get_form_kwargs(**kwargs)
        kwargs['gerente'] = self.request.user  # se envia al formulario el username del gerente
        return kwargs

    def form_valid(self, form):
        """

        Función que valida los campos requeridos fueron completados y los guarda en la base de datos.<br/>
        **:param form:** recibe el formulario con los datos.<br/>
        **:return:** redirige a la instancia del modelo proyecto en la plantilla de detalles de proyecto.<br/>

        """
        object = form.save()
        return redirect('proyecto:detail', pk=object.pk)


# === delete project ===
class DeleteProject(LoginRequiredMixin, DeleteView, PermissionRequiredMixin):
    """
    Permite suprimir una instancia del modelo de Proyecto.<br/>
    **:param PermissionRequiredMixin:** Libreria que gestiona el permiso para la creación de proyectos.El usuario
    debe poseer el permiso correspondiente de eliminar proyectos.<br/>
    **:param LoginRequiredMixin:** Requiere estar logueado, de la libreria django.contrib.auth.mixins<br/>
    **:param DeleteView:** Recibe una vista generica de tipo DeleteView para vistas basadas en clases.<br/>
    **:return:** Eliminar una instancia del modelo Proyecto, luego se redirige a la lista de proyectos.<br/>
    """
    model = Proyecto
    template_name = 'proyecto/delete.html'
    permission_required = 'proyecto.eliminar_proyecto'
    success_url = reverse_lazy('proyecto:list')


# === detail project ===
class DetailProject(LoginRequiredMixin, DetailView, PermissionRequiredMixin):
    """
    Despliega los detalles de una instancia del modelo de Proyecto.<br/>
    **:param PermissionRequiredMixin:** Libreria que gestiona el permiso para la creación de proyectos.El usuario
    debe poseer el permiso correspondiente de eliminar proyectos.<br/>
    **:param LoginRequiredMixin:** Requiere estar logueado, de la libreria django.contrib.auth.mixins<br/>
    **:param DetailView:** Recibe una vista generica de tipo DetailView para vistas basadas en clases.<br/>
    **:return:** Despliega los detalles de una instancia del modelo Proyecto.<br/>
    """
    model = Proyecto
    template_name = 'proyecto/detail.html'
    permission_required = 'proyecto.detalles_proyecto'
    success_url = reverse_lazy('proyecto:list')


def render_pdf_view(request, id_proyecto):
    """
       Permite generar un reporte en pdf de todos los items en estado desarrollo de un proyecto<br/>
       **:param request:**Recibe un request por parte de un usuario.<br/>
       **:param pk:**Recibe el pk del comite que se desea emitir el reporte.<br/>
       **:return:** La vista preliminar de los items en estado desarrollo en formato de pdf para descargar el reporte.<br/>
       """
    template_path = 'proyecto/reporte.html'
    item_queryset = Item.objects.none()
    for fase in Fase.objects.filter(proyecto=id_proyecto):  # Queryset de los item del proyecto
        item_queryset |= Item.objects.filter(fase=fase.pk).exclude(estado='Aprobado')

    print(item_queryset)
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    context = {'items': item_queryset, 'proyecto': proyecto, }
    # context = {'myvar': 'this is your template context'}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # if download :
    # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # if view_pdf:
    response['Content-Disposition'] = 'filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

# **Volver atras** : [[urls.py]]

# **Ir al principio ** :[[admin.py]]

# === Indice de la documentación de la Aplicación Proyecto  === <br/>
# 1.admin   : [[admin.py]]<br/>
# 2.apps    : [[apps.py]]<br/>
# 3.forms   : [[forms.py]]<br/>
# 4.models  : [[models.py]]<br/>
# 5.tests   : [[tests.py]]<br/>
# 6.urls    : [[urls.py]]<br/>
# 7.views   : [[views.py]]<br/>

# Regresar al menu principal : [Menú Principal](../../docs-index/index.html)
