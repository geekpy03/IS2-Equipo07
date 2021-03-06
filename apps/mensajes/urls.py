# === Importamos las vistas basadas en clases y en funciones del codigo fuente de views.py ===
from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required
from apps.mensajes.views import Mensajes, ActualizarUsuarioMensaje, EliminarUsuarioMensaje


# **Vistas **

# **1.Listar Mensajes    :** Vista que despliega los usuarios recientemente registrados como nuevo<br/>
# **2.Modificar usuario  :** Vista que despliega la actualización de usuarios<br/>
# **3.Eliminar usuario   :** Vista que despliega rechazar a ese usuario<br/>
urlpatterns = [
    url(r'^lista/', login_required(permission_required('usuario.ver_mensaje',raise_exception=True)(Mensajes.as_view())), name='mensaje_lista'),
    url(r'^notificaciones/(?P<pk>\d+)/$', login_required(permission_required('usuario.mensaje_editar', raise_exception=True)(ActualizarUsuarioMensaje.as_view())), name='mensaje_usuario_modificar'),
    url(r'^rechazar/(?P<pk>\d+)/$', login_required(permission_required('usuario.mensaje_rechazar', raise_exception=True)(EliminarUsuarioMensaje.as_view())), name='mensaje_usuario_eliminar'),
]
# **Volver atras** :[[tests.py]]
# **Ir a la documentación del vistas de la Aplicación** :[[forms.py]]

# === Indice de la documentación de la Aplicación mensajes  === <br/>
# 1.apps                : [[apps.py]]<br/>
# 2.context_processors  : [[context_processors.py]]<br/>
# 3.test                : [[tests.py]]<br/>
# 4.urls                : [[urls.py]]<br/>
# 5.views               : [[views.py]]<br/>

# Regresar al menu principal : [Menú Principal](../../docs-index/index.html)