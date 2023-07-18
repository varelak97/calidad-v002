from ._anvil_designer import CALIDAD_CONTROLDOCUMENTOSTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class CALIDAD_CONTROLDOCUMENTOS(CALIDAD_CONTROLDOCUMENTOSTemplate):
  
  def __init__(self, datos, **properties):
    self.init_components(**properties)
    self.datos = datos
    
  def button_volver_click(self, **event_args):
    self.datos['clave_form'] = 'CALIDAD'
    self.parent.raise_event('x-actualizar_form_activo', datos=self.datos)

