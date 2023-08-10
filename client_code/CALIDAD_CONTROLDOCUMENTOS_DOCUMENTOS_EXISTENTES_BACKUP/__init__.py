from ._anvil_designer import CALIDAD_CONTROLDOCUMENTOS_DOCUMENTOS_EXISTENTES_BACKUPTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class CALIDAD_CONTROLDOCUMENTOS_DOCUMENTOS_EXISTENTES_BACKUP(CALIDAD_CONTROLDOCUMENTOS_DOCUMENTOS_EXISTENTES_BACKUPTemplate):
  datos = {}
  def __init__(self, datos, **properties):
    self.init_components(**properties)
    self.datos = datos
    self.repeating_panel_documentos_existentes.items = anvil.server.call('obtener_documentos_existentes')
    
  def button_volver_click(self, **event_args):
    self.content_panel.visible = False
    self.datos['clave_form'] = 'CALIDAD_CONTROLDOCUMENTOS'
    self.parent.raise_event('x-actualizar_form_activo', datos=self.datos)
    self.content_panel.visible = True