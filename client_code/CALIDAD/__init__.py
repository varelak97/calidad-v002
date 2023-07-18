from ._anvil_designer import CALIDADTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class CALIDAD(CALIDADTemplate):
  datos = {}
  def __init__(self, datos, **properties):
    self.init_components(**properties)
    self.datos = datos
  
  def link_control_documentos_click(self, **event_args):
    self.datos['clave_form'] = 'CALIDAD_CONTROLDOCUMENTOS'
    self.parent.raise_event('x-actualizar_form_activo', datos=self.datos)

