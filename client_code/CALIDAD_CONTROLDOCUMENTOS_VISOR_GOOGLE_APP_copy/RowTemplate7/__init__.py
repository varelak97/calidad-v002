from ._anvil_designer import RowTemplate7Template
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class RowTemplate7(RowTemplate7Template):
  data_row_panel_indicador = []
  def __init__(self, **properties):
    self.init_components(**properties)
    self.data_row_panel_indicador = [
      self.label_indicador_partida,
      self.label_pregunta,
      self.label_descripcion,
      self.label_tipo_entrada,
      self.label_filas,
      self.label_columnas,
      self.button_editar,
      self.button_eliminar
    ]

  def button_editar_click(self, **event_args):
    for componente in self.data_row_panel_indicador:
      componente.visible = False
    
    self.data_row_panel_editable.background = "theme:Yellow"
    self.data_row_panel_editable.visible = True

  def button_guardar_click(self, **event_args):
    """This method is called when the button is clicked"""
    #Aquí debe mandar el diccionario al form padre y desde ahí actualizar el repeating panel
    
    pass

