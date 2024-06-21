from ._anvil_designer import CALIDAD_CONTROLDOCUMENTOSTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class CALIDAD_CONTROLDOCUMENTOS(CALIDAD_CONTROLDOCUMENTOSTemplate):
  datos = {}
  def __init__(self, datos, **properties):
    self.init_components(**properties)
    self.datos = datos
    """if self.datos['id_usuario_erp'] not in [18]: #user paco: 404, id_usuario_erp: 12, pass: 181300
      self.button_documentos_existentes.enabled = False
      self.button_nuevo_documento.enabled = False
      self.label_titulo_seccion_control_de_documentos.text = "MÓDULO NO DISPONIBLE"""
    
  def button_volver_click(self, **event_args):
    self.content_panel.visible = False
    self.datos['clave_form'] = 'CALIDAD'
    self.parent.raise_event('x-actualizar_form_activo', datos=self.datos)
    self.content_panel.visible = True
    
  def button_nuevo_documento_click(self, **event_args):
    self.content_panel.visible = False
    with Notification("Revisando documentos que puedes generar. Por favor, espera un momento...", title = "PROCESANDO PETICIÓN"):
      bandera_pertenencia_a_equipo = anvil.server.call('verificacion_pertenencia_a_equipo', self.datos['id_usuario_erp'])
      
      if bandera_pertenencia_a_equipo:
        self.datos['clave_form'] = "CALIDAD_CONTROLDOCUMENTOS_NUEVO_DOCUMENTO"
        self.parent.raise_event('x-actualizar_form_activo', datos=self.datos)
      
      else:
        alert(
          content = "Actualmente no formas parte de un equipo para poder generar documentos. Solicita a tu jefe inmediato (o líder de equipo) que envíe una solicitud al departamento de Sistemas y TI para darte los privilegios correspondientes",
          title = "ACCIÓN DENEGADA",
          large = True,
          dismissible = False
        )
    self.content_panel.visible = True

  def button_documentos_existentes_click(self, **event_args):
    self.content_panel.visible = False
    self.datos['clave_form'] = "CALIDAD_CONTROLDOCUMENTOS_DOCUMENTOS_EXISTENTES"
    self.parent.raise_event('x-actualizar_form_activo', datos=self.datos)
    self.content_panel.visible = True

