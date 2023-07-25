from ._anvil_designer import RowTemplate5Template
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class RowTemplate5(RowTemplate5Template):
  def __init__(self, **properties):
    self.init_components(**properties)

  def button_opciones_click(self, **event_args):
    id_usuario_erp = self.parent.parent.parent.parent.parent.datos['id_usuario_erp']
    botones = [
        ("ACCEDER AL DOCUMENTO", "CALIDAD_CONTROLDOCUMENTOS_VISOR_GOOGLE_APP"),
        ("HISTORIAL DE MODIFICACIONES", "CALIDAD_CONTROLDOCUMENTOS_HISTORIAL")
      ]
    if self.label_status.text == "LIBERADO":
      #AQUÍ VOY
      pass
      
    evento = alert(
      content = "",
      title = "ELIGE UNA OPERACIÓN",
      buttons = [
        ("ACCEDER AL DOCUMENTO", "CALIDAD_CONTROLDOCUMENTOS_VISOR_GOOGLE_APP"),
        ("HISTORIAL DE MODIFICACIONES", "CALIDAD_CONTROLDOCUMENTOS_HISTORIAL")
      ]
    )
    if evento != None:
      datos = {
        'id_usuario_erp': id_usuario_erp,
        'clave_form': evento,
        'id_registro_documento': anvil.server.call('obtener_id_registro', self.label_nombre_documento.text)
      }
      self.parent.parent.parent.parent.parent.raise_event('x-actualizar_form_activo', datos=datos)