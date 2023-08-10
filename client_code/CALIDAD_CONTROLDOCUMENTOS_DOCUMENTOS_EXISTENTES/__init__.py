from ._anvil_designer import CALIDAD_CONTROLDOCUMENTOS_DOCUMENTOS_EXISTENTESTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import date

class CALIDAD_CONTROLDOCUMENTOS_DOCUMENTOS_EXISTENTES(CALIDAD_CONTROLDOCUMENTOS_DOCUMENTOS_EXISTENTESTemplate):
  datos = {}
  lista_buttons_ordenamiento = []
  items = []
  def __init__(self, datos, **properties):
    self.init_components(**properties)
    self.datos = datos
    self.items = list(anvil.server.call('obtener_documentos_existentes'))
    self.repeating_panel_documentos_existentes.items = self.items
    
    self.lista_buttons_ordenamiento = [
      self.button_nombre_completo,
      self.button_fecha_emision,
      self.button_propietario,
      self.button_documento_base
    ]

    

  def button_volver_click(self, **event_args):
    self.content_panel.visible = False
    self.datos['clave_form'] = 'CALIDAD_CONTROLDOCUMENTOS'
    self.parent.raise_event('x-actualizar_form_activo', datos=self.datos)
    self.content_panel.visible = True

  def actualizar_lista_documentos_existentes(self, **event_args):
    items = self.items.copy()
    if self.drop_down_estado.selected_value != None:
      items = [item for item in items if item['status'].upper() == self.drop_down_estado.selected_value]
    if self.drop_down_nivel.selected_value != None:
      items = [item for item in items if item['nivel'] == int(self.drop_down_nivel.selected_value)]
    if self.drop_down_tipo_documento.selected_value != None:
      items = [item for item in items if item['tipo_documento'] == self.drop_down_tipo_documento.selected_value]
    #FALTA CHECAR ÁREAS
    if self.drop_down_tipo_archivo.selected_value != None:
      items = [item for item in items if item['tipo_archivo'] == self.drop_down_tipo_archivo.selected_value]
    if self.drop_down_fecha_emision.selected_value != None:
      if self.drop_down_fecha_emision.selected_value == "SIN FECHA":
        items = [item for item in items if item['fecha_emision'] in ("",None)]
      elif self.drop_down_fecha_emision.selected_value == "UNA FECHA":
        if self.date_picker_fecha_1.date != None:
          items = [item for item in items if item['fecha_emision'] == self.date_picker_fecha_1.date]
      elif self.drop_down_fecha_emision.selected_value == "ENTRE DOS FECHAS":
        if self.date_picker_fecha_2.date != None:
          items = [item for item in items if item['fecha_emision'] != None and item['fecha_emision'] >= self.date_picker_fecha_1.date and item['fecha_emision'] <= self.date_picker_fecha_2.date]
    if len(self.text_box_nombre_completo.text) > 0:
      items = [item for item in items if self.text_box_nombre_completo.text in item['nombre_completo']]
    if len(self.text_box_propietario.text) > 0:
      items = [item for item in items if self.text_box_propietario.text in item['propietario']]
    #FALTA DOCUMENTO BASE
    
    self.repeating_panel_documentos_existentes.items = items
    self.ordenar_lista_documentos_existentes()
      
  def ordenar_lista_documentos_existentes(self, **event_args):
    for button in self.lista_buttons_ordenamiento:
      if button.icon != 'fa:circle-o':
        tag_ordenamiento = button.tag
        ban_reverse = True if button.icon == 'fa:arrow-circle-up' else False
        break
    items = sorted(list(self.repeating_panel_documentos_existentes.items), key=lambda d:d[tag_ordenamiento], reverse=ban_reverse)
    self.repeating_panel_documentos_existentes.items = items

  def actualizar_botones_ordenamiento(self, boton_protagonista):
    for boton in self.lista_buttons_ordenamiento:
      if boton == boton_protagonista:
        if boton.icon in ('fa:circle-o', 'fa:arrow-circle-up'):
          boton.icon = 'fa:arrow-circle-down'
        elif boton.icon == 'fa:arrow-circle-down':
          boton.icon = 'fa:arrow-circle-up'
      else:
        boton.icon = 'fa:circle-o'
    self.ordenar_lista_documentos_existentes()

  def text_box_documento_change(self, **event_args):
    self.actualizar_lista_documentos_existentes()

  def drop_down_estado_change(self, **event_args):
    self.actualizar_lista_documentos_existentes()

  def drop_down_nivel_change(self, **event_args):
    self.actualizar_lista_documentos_existentes()

  def drop_down_tipo_documento_change(self, **event_args):
    self.actualizar_lista_documentos_existentes()

  def drop_down_area_change(self, **event_args):
    self.actualizar_lista_documentos_existentes()

  def drop_down_tipo_archivo_change(self, **event_args):
    self.actualizar_lista_documentos_existentes()

  def drop_down_fecha_emision_change(self, **event_args):
    if self.drop_down_fecha_emision.selected_value in (None,"SIN FECHA"):
      self.date_picker_fecha_1.date = None
      self.date_picker_fecha_1.visible = False
      self.date_picker_fecha_2.date = None
      self.date_picker_fecha_2.visible = False
      self.actualizar_lista_documentos_existentes()
    else:
      self.date_picker_fecha_1.visible = True
      if self.drop_down_fecha_emision.selected_value == "ENTRE DOS FECHAS":
        self.date_picker_fecha_2.visible = True

  def date_picker_fecha_1_change(self, **event_args):
    self.date_picker_fecha_1.date = self.date_picker_fecha_1.date
    if self.date_picker_fecha_1.date != None:
      if self.drop_down_fecha_emision.selected_value == "UNA FECHA":
        self.actualizar_lista_documentos_existentes()
      elif self.drop_down_fecha_emision.selected_value == "ENTRE DOS FECHAS":
        self.date_picker_fecha_2_change()

  def date_picker_fecha_2_change(self, **event_args):
    self.date_picker_fecha_2.date = self.date_picker_fecha_2.date
    if self.date_picker_fecha_1.date != None and self.date_picker_fecha_2.date != None:
      if self.date_picker_fecha_2.date > self.date_picker_fecha_1.date:
        self.actualizar_lista_documentos_existentes()
      else:
        Notification("La segunda fecha debe ser posterior o igual a la primera", title="ERROR", style="danger")

  def text_box_propietario_change(self, **event_args):
    self.actualizar_lista_documentos_existentes()

  def text_box_documento_base_change(self, **event_args):
    self.actualizar_lista_documentos_existentes()
    
  def button_nombre_completo_click(self, **event_args):
    self.actualizar_botones_ordenamiento(self.button_nombre_completo)

  def button_fecha_emision_click(self, **event_args):
    self.actualizar_botones_ordenamiento(self.button_fecha_emision)

  def button_propietario_click(self, **event_args):
    self.actualizar_botones_ordenamiento(self.button_propietario)

  def button_documento_base_click(self, **event_args):
    self.actualizar_botones_ordenamiento(self.button_documento_base)

  def button_borrar_filtros_click(self, **event_args):
    self.text_box_nombre_completo.text = ""
    self.drop_down_estado.selected_value = None
    self.drop_down_nivel.selected_value = None
    self.drop_down_tipo_documento.selected_value = None
    self.drop_down_area.selected_value = None
    self.drop_down_tipo_archivo.selected_value = None
    self.drop_down_fecha_emision.selected_value = None
    self.drop_down_fecha_emision_change()
    self.text_box_propietario.text = ""
    self.text_box_documento_base.text = ""
    self.button_nombre_completo.icon = None
    self.actualizar_lista_documentos_existentes()
    self.button_nombre_completo_click()

  


  

    




        
        
    
    







