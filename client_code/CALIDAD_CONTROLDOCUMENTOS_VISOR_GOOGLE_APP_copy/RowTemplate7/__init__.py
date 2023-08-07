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
      self.link_archivo,
      self.label_tipo_entrada,
      self.label_filas,
      self.label_columnas,
      self.button_editar,
      self.button_eliminar
    ]

  def button_editar_click(self, **event_args):
    for componente in self.data_row_panel_indicador:
      componente.visible = False
    if self.link_archivo.text == '':
      self.file_loader_archivo.text = "SUBIR"
      self.button_eliminar_archivo.visible = False
    else:
      self.file_loader_archivo.text = self.link_archivo.text
      self.button_eliminar_archivo.visible = True
      
    self.data_row_panel_editable.background = "theme:Yellow"
    self.data_row_panel_editable.visible = True

  def button_guardar_click(self, **event_args):
    """This method is called when the button is clicked"""
    #Aquí debe mandar el diccionario al form padre y desde ahí actualizar el repeating panel
    item = {
      'partida': int(self.label_editable_partida.text),
      'pregunta': self.text_area_pregunta.text,
      'descripcion': self.text_area_descripcion.text,
      'archivo': self.file_loader_archivo.file,
      'tipo_entrada': self.drop_down_tipo_entrada.selected_value,
      'filas': self.text_area_filas.text,
      'columnas': self.text_area_columnas.text
    }
    if self.file_loader_archivo.text == 'SUBIR':
      item['nombre_archivo'] = ''
    else:
      item['nombre_archivo'] = self.file_loader_archivo.file.name
    for componente in self.data_row_panel_indicador:
      componente.visible = True
    self.data_row_panel_editable.visible = False
    self.data_row_panel_editable.background = None
    self.parent.parent.parent.parent.raise_event('x-actualizar_item', item = item)
    pass

  def file_loader_archivo_change(self, file, **event_args):
    if len(self.file_loader_archivo.files) > 0:
      self.file_loader_archivo.text = self.file_loader_archivo.file.name
      self.button_eliminar_archivo.visible = True
    else:
      self.file_loader_archivo.text = "SUBIR"
      self.button_eliminar_archivo.visible = False

  def button_eliminar_archivo_click(self, **event_args):
    self.file_loader_archivo.clear()
    self.file_loader_archivo_change(None)



