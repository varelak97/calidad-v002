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
    
  def button_volver_click(self, **event_args):
    self.datos['clave_form'] = 'CALIDAD'
    self.parent.raise_event('x-actualizar_form_activo', datos=self.datos)

  def button_nuevo_documento_click(self, **event_args):
    with Notification("Revisando documentos que puedes generar. Por favor, espera un momento...", title = "PROCESANDO PETICIÓN"):
      validadores = anvil.server.call('obtener_lista_id_validadores')
      if self.datos['id_usuario_erp'] in validadores:
        self.datos['clave_form'] = "CALIDAD_CONTROLDOCUMENTOS_NUEVO_DOCUMENTO"
        self.parent.raise_event('x-actualizar_form_activo', datos=self.datos)
      else:
        info_validadores = anvil.server.call('obtener_nombres_validadores_por_area')
        alert(
          content = f"No estás registrado como autor (validador final) de documentos de ningún área.\nSi deseas trabajar en un nuevo documento, solicita al responsable del area correspondiente:\n{info_validadores}",
          title = "ACCIÓN DENEGADA",
          large = True,
          dismissible = False
        )

  def button_documentos_existentes_click(self, **event_args):
    self.datos['clave_form'] = "CALIDAD_CONTROLDOCUMENTOS_DOCUMENTOS_EXISTENTES"
    self.parent.raise_event('x-actualizar_form_activo', datos=self.datos)


