from ._anvil_designer import CALIDAD_CONTROLDOCUMENTOS_VISOR_GOOGLE_APPTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil.js.window import jQuery
from anvil.js import get_dom_node
from datetime import datetime, date
from time import sleep

class CALIDAD_CONTROLDOCUMENTOS_VISOR_GOOGLE_APP(CALIDAD_CONTROLDOCUMENTOS_VISOR_GOOGLE_APPTemplate):
  datos = {}
  componentes_deshabilitables = []
  componentes_deshabilitables_condicionados = []
  
  def __init__(self, datos, **properties):
    self.init_components(**properties)
    self.datos = datos
    
    self.componentes_deshabilitables = [
      self.button_volver,
      self.link_sin_visualizacion,
      self.button_actualizar,
      self.column_panel_visor_app_google
    ]

    self.componentes_deshabilitables_condicionados = [
      self.button_enviar_a_revision,
      self.button_aprobar,
      self.button_aprobar_revision_y_liberar,
      self.button_rechazar
    ]
    
    self.datos.update(anvil.server.call('obtener_renglon_documento', self.datos['id_registro_documento']))
    self.label_codigo_documento.text = self.datos['nombre_completo']
    self.label_status.text = f"Estado: {self.datos['status']}"
    if self.datos['status'] == 'Rechazado':
      self.text_area_motivo_rechazo.text = self.datos['comentarios_renglon'][19:]
      self.flow_panel_motivo_rechazo.visible = True
    self.agregar_visor_app_google()
    if self.datos['status'] in ("En creación", "Rechazado") and self.datos['id_usuario_erp'] in self.datos['creadores']:
      self.button_enviar_a_revision.visible = True
    elif (self.datos['status'] in ("En revisión") and self.datos['id_usuario_erp'] in self.datos['revisores']) or ((self.datos['status'] in ("En validación") and self.datos['id_usuario_erp'] in self.datos['validadores'])):
      self.flow_panel_aprobacion_rechazo.visible = True
    if self.datos['status'] == "En revisión" and self.datos['id_usuario_erp'] in self.datos['revisores']:
      if self.datos['id_usuario_erp'] in self.datos['validadores']:
        self.button_aprobar.text = "APROBAR SÓLO REVISIÓN"
        self.button_aprobar_revision_y_liberar.visible = True
    elif self.datos['status'] == "En validación":
      self.button_aprobar.text = "LIBERAR"

  def habilitacion_general_componentes(self, bandera):
    for componente in self.componentes_deshabilitables:
      if componente in (Button, Link):
        componente.enabled = bandera
      elif componente is ColumnPanel:
        componente.visible = bandera
  
  def button_volver_click(self, **event_args):
    self.datos['clave_form'] = 'CALIDAD_CONTROLDOCUMENTOS_DOCUMENTOS_EXISTENTES'
    self.parent.raise_event('x-actualizar_form_activo', datos=self.datos)
      
  def agregar_visor_app_google(self, **event_args):
    tipo_google_app = anvil.server.call('tipo_google_app', self.datos['tipo_app'])
    self.iframe = jQuery("<iframe width='100%' height='800px'>").attr("src",f"https://docs.google.com/{tipo_google_app}/d/{self.datos['id_google']}/edit?usp=sharing?&embedded=true")
    self.iframe.appendTo(get_dom_node(self.column_panel_visor_app_google))

  def link_sin_visualizacion_click(self, **event_args):
    self.link_sin_visualizacion.visible = False
    self.column_panel_sin_visualizacion.visible = True

  def button_actualizar_click(self, **event_args):
    self.column_panel_visor_app_google.clear()
    self.agregar_visor_app_google()
    self.column_panel_sin_visualizacion.visible = False
    self.link_sin_visualizacion.visible = True

  def button_enviar_a_revision_click(self, **event_args):
    self.datos['id_usuario_registrador'] = self.datos['id_usuario_erp']
    self.datos['marca_temporal'] = datetime.now()
    with Notification("Enviando documento a revisión. Por favor espera...", title="PROCESANDO PETICIÓN"):
      respuesta = anvil.server.call('enviar_documento_a_revision', self.datos)
    sleep(1)
    if respuesta[0]:
      Notification(f"El documento {self.datos['codigo']} ha sido enviado a revisión satisfactoriamente.", title="¡ÉXITO!", style='success').show()
      with Notification("Enviando correo electrónico de notificación al equipo de trabajo asignado. Por favor espera...", title = "NOTIFICACIÓN POR CORREO ELECTRÓNICO"):
        respuesta_envio_email = anvil.server.call(
          'enviar_email_notificacion',
          {
            'id_registro_documento': respuesta[1],
            'operacion': 'revisión'
          }
        )
        if not respuesta_envio_email[0]:
          equipo_de_trabajo = {
            'creadores': [],
            'revisores': self.datos['revisores'],
            'validadores': []
          }
          equipo_trabajo_id_usuarios_erp = anvil.server.call('obtener_nombres_equipo_de_trabajo', equipo_de_trabajo)
          revisores = ""
          for revisor in equipo_trabajo_id_usuarios_erp['revisores']:
            revisores += f"\n•{revisor}" 
          alert(
            content = f"El documento fue enviado a revisión satisfactoriamente, pero no fue posible enviar su respectiva notificación por correo electrónico al equipo de trabajo.\n\n{respuesta_envio_email[1]}\n\nPor favor informa a la(s) siguiente(s) persona(s) que la revisión del documento ya está disponible para ser aprobada o rechazada:{revisores}",
            title = "ERROR DURANTE ENVÍO DE NOTIFICACIÓN",
            large=True,
            dismissible=False
          )
        else:
          Notification("Notificación a equipo de trabajo enviada por correo electrónico", title="¡ÉXITO!", style='success').show()
          sleep(2)
      Notification("Por favor espera...", title="REDIRIGIENDO")
      self.datos = {
        'id_usuario_erp': self.datos['id_usuario_erp'],
        'clave_form': 'CALIDAD_CONTROLDOCUMENTOS_DOCUMENTOS_EXISTENTES'
      }
      self.parent.raise_event('x-actualizar_form_activo', datos=self.datos)
    else:
      alert(
        content = respuesta[1] + f"\n\nConfirma que tu dispositivo (PC, laptop o tablet) esté conectado a una red con acceso estable a internet e inténtalo nuevamente. Si el problema persiste, contacta al departamento de Sistemas.",
        title = "OCURRIÓ UN ERROR",
        dismissible=False
      )
      
  def button_aprobar_click(self, **event_args):
    if self.datos['status'] == "En revisión":
      with Notification("Enviando documento a validación. Por favor espera...", title="PROCESANDO PETICIÓN"):
        self.datos['id_usuario_registrador'] = self.datos['id_usuario_erp']
        self.datos['marca_temporal'] = datetime.now()
        respuesta = anvil.server.call('enviar_documento_a_validacion', self.datos)
      sleep(1)
      if respuesta[0]:
        Notification(f"El documento {self.datos['codigo']} ha sido enviado a validación final satisfactoriamente.", title="¡ÉXITO!", style='success').show()
        with Notification("Enviando correo electrónico de notificación al equipo de trabajo asignado. Por favor espera...", title = "NOTIFICACIÓN POR CORREO ELECTRÓNICO"):
          respuesta_envio_email = anvil.server.call(
            'enviar_email_notificacion',
            {
              'id_registro_documento': respuesta[1],
              'operacion': 'validación'
            }
          )
          if not respuesta_envio_email[0]:
            equipo_de_trabajo = {
              'creadores': [],
              'revisores': [],
              'validadores': self.datos['validadores']
            }
            equipo_trabajo_id_usuarios_erp = anvil.server.call('obtener_nombres_equipo_de_trabajo', equipo_de_trabajo)
            validadores = ""
            for validador in equipo_trabajo_id_usuarios_erp['validadores']:
              validadores += f"\n•{validador}" 
            alert(
              content = f"El documento fue enviado a validación final satisfactoriamente, pero no fue posible enviar su respectiva notificación por correo electrónico al equipo de trabajo.\n\n{respuesta_envio_email[1]}\n\nPor favor informa a la(s) siguiente(s) persona(s) que la revisión del documento ya está disponible para ser aprobada o rechazada:{validadores}",
              title = "ERROR DURANTE ENVÍO DE NOTIFICACIÓN",
              large=True,
              dismissible=False
            )
          else:
            Notification("Notificación a equipo de trabajo enviada por correo electrónico", title="¡ÉXITO!", style='success').show()
            sleep(2)
        Notification("Por favor espera...", title="REDIRIGIENDO")
        self.datos = {
          'id_usuario_erp': self.datos['id_usuario_erp'],
          'clave_form': 'CALIDAD_CONTROLDOCUMENTOS_DOCUMENTOS_EXISTENTES',
        }
        self.parent.raise_event('x-actualizar_form_activo', datos=self.datos)
      else:
        alert(
          content = respuesta[1] + f"\n\nConfirma que tu dispositivo (PC, laptop o tablet) esté conectado a una red con acceso estable a internet e inténtalo nuevamente. Si el problema persiste, contacta al departamento de Sistemas.",
          title = "OCURRIÓ UN ERROR",
          dismissible=False
        )
    elif self.datos['status'] == "En validación":
      self.liberar_documento()

  def button_aprobar_revision_y_liberar_click(self, **event_args):
    self.liberar_documento()
  
  def liberar_documento(self, **event_args):
    self.datos['id_usuario_registrador'] = self.datos['id_usuario_erp']
    self.datos['marca_temporal'] = datetime.now()
    self.datos['fecha_emision'] = date.today()
    
    with Notification("Liberando documento. Por favor espera...", title="PROCESANDO PETICIÓN"):
      respuesta = anvil.server.call('liberar_documento', self.datos)
    sleep(1)
    if respuesta[0]:
      Notification(f"El documento {self.datos['codigo']} ha sido liberado satisfactoriamente y está listo para su uso productivo.", title="¡ÉXITO!", style='success').show()
      with Notification("Enviando correo electrónico de notificación al equipo de trabajo asignado. Por favor espera...", title = "NOTIFICACIÓN POR CORREO ELECTRÓNICO"):
        respuesta_envio_email = anvil.server.call(
          'enviar_email_notificacion',
          {
            'id_registro_documento': respuesta[1],
            'operacion': 'Liberación'
          }
        )
        if not respuesta_envio_email[0]:
          alert(
            content = f"El documento fue liberado satisfactoriamente, pero no fue posible enviar su respectiva notificación por correo electrónico al equipo de trabajo.\n\n{respuesta_envio_email[1]}\n\nPor favor informa al equipo de trabajo que ya pueden usar este documento a nivel productivo.",
            title = "ERROR DURANTE ENVÍO DE NOTIFICACIÓN",
            large=True,
            dismissible=False
          )
        else:
          Notification("Notificación a equipo de trabajo enviada por correo electrónico", title="¡ÉXITO!", style='success').show()
          sleep(2)
      Notification("Por favor espera...", title="REDIRIGIENDO")
      self.datos = {
        'id_usuario_erp': self.datos['id_usuario_erp'],
        'clave_form': 'CALIDAD_CONTROLDOCUMENTOS_DOCUMENTOS_EXISTENTES'
      }
      self.parent.raise_event('x-actualizar_form_activo', datos=self.datos)
    else:
      alert(
        content = respuesta[1] + f"\n\nConfirma que tu dispositivo (PC, laptop o tablet) esté conectado a una red con acceso estable a internet e inténtalo nuevamente. Si el problema persiste, contacta al departamento de Sistemas.",
        title = "OCURRIÓ UN ERROR",
        dismissible=False
      )
    
  def button_rechazar_click(self, **event_args):
    card = ColumnPanel(role='elevated-card')
    text_area = TextArea(auto_expand=True,height=100,role='outlined')
    card.add_component(text_area)
    while True:
      respuesta = alert(
        content = card,
        title = "MOTIVO DEL RECHAZO:",
        buttons = [
          ("CONFIRMAR RECHAZO", True),
          ("CANCELAR", False)
        ],
        dismissible = False,
        large = True
      )
      while "  " in text_area.text:
        text_area.text = str(text_area.text).replace("  "," ")
      text_area.text = str(text_area.text).strip()
      if (not respuesta) or (respuesta and len(text_area.text) > 0):
        break
      else:
        alert("Es necesario dejar comentarios que especifiquen el motivo del rechazo.", title="ACCIÓN DENEGADA")
    if respuesta:
      self.datos['motivo_rechazo'] = text_area.text
      self.datos['id_usuario_registrador'] = self.datos['id_usuario_erp']
      self.datos['marca_temporal'] = datetime.now()
      with Notification("Devolviendo documento a etapa inicial de creación. Por favor espera...", title="PROCESANDO PETICIÓN"):
        respuesta = anvil.server.call('rechazar_documento', self.datos)
      sleep(1)
      if respuesta[0]:
        Notification(f"El documento {self.datos['codigo']} ha sido rechazado satisfactoriamente.", title="¡ÉXITO!", style='success').show()
        with Notification("Enviando correo electrónico de notificación al equipo de trabajo asignado. Por favor espera...", title = "NOTIFICACIÓN POR CORREO ELECTRÓNICO"):
          respuesta_envio_email = anvil.server.call(
            'enviar_email_notificacion',
            {
              'id_registro_documento': respuesta[1],
              'operacion': 'Rechazo',
              'motivo_rechazo': text_area.text,
              'origen_rechazo': str(self.label_status.text).split()[-1]
            }
          )
          if not respuesta_envio_email[0]:
            equipo_de_trabajo = {
              'creadores': self.datos['creadores'],
              'revisores': [],
              'validadores': []
            }
            equipo_trabajo_id_usuarios_erp = anvil.server.call('obtener_nombres_equipo_de_trabajo', equipo_de_trabajo)
            creadores = ""
            for creador in equipo_trabajo_id_usuarios_erp['creadores']:
              creadores += f"\n•{creador}" 
            alert(
              content = f"El documento fue rechazado satisfactoriamente, pero no fue posible enviar su respectiva notificación por correo electrónico al equipo de trabajo.\n\n{respuesta_envio_email[1]}\n\nPor favor informa a la(s) siguiente(s) persona(s) que el documento ha sido nuevamente habilitado para edición:{creadores}",
              title = "ERROR DURANTE ENVÍO DE NOTIFICACIÓN",
              large=True,
              dismissible=False
            )
          else:
            Notification("Notificación a equipo de trabajo enviada por correo electrónico", title="¡ÉXITO!", style='success').show()
            sleep(2)
        Notification("Por favor espera...", title="REDIRIGIENDO")
        self.datos = {
          'id_usuario_erp': self.datos['id_usuario_erp'],
          'clave_form': 'CALIDAD_CONTROLDOCUMENTOS_DOCUMENTOS_EXISTENTES',
        }
        self.parent.raise_event('x-actualizar_form_activo', datos=self.datos)
      else:
        alert(
          content = respuesta[1] + f"\n\nConfirma que tu dispositivo (PC, laptop o tablet) esté conectado a una red con acceso estable a internet e inténtalo nuevamente. Si el problema persiste, contacta al departamento de Sistemas.",
          title = "OCURRIÓ UN ERROR",
          dismissible=False
        )

  def link_detalles_encabezado_click(self, **event_args):
    if "OCULTAR" in str(self.link_detalles_encabezado.text):
      self.column_panel_detalles_encabezado.visible = False
      self.link_detalles_encabezado.text = str(self.link_detalles_encabezado.text).replace('OCULTAR','MOSTRAR')
    else:
      self.column_panel_detalles_encabezado.visible = True
      self.link_detalles_encabezado.text = str(self.link_detalles_encabezado.text).replace('MOSTRAR','OCULTAR')
      