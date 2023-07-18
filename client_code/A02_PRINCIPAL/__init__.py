from ._anvil_designer import A02_PRINCIPALTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

#IMPORTACIÓN DE FORMS DE MÓDULOS EXTERNOS:
from ..CALIDAD import CALIDAD
from ..CALIDAD_CONTROLDOCUMENTOS import CALIDAD_CONTROLDOCUMENTOS
from ..CALIDAD_CONTROLDOCUMENTOS_DOCUMENTOS_EXISTENTES import CALIDAD_CONTROLDOCUMENTOS_DOCUMENTOS_EXISTENTES
from ..CALIDAD_CONTROLDOCUMENTOS_HISTORIAL import CALIDAD_CONTROLDOCUMENTOS_HISTORIAL
from ..CALIDAD_CONTROLDOCUMENTOS_NUEVO_DOCUMENTO import CALIDAD_CONTROLDOCUMENTOS_NUEVO_DOCUMENTO
from ..CALIDAD_CONTROLDOCUMENTOS_VISOR_GOOGLE_APP import CALIDAD_CONTROLDOCUMENTOS_VISOR_GOOGLE_APP

class A02_PRINCIPAL(A02_PRINCIPALTemplate):
  datos = {}
  form_activo = None
  
  def __init__(self, datos, **properties):
    self.init_components(**properties)

    #--- INICIALIZACIÓN DE VARIABLES "GLOBALES" ---
    self.datos = datos

    #--- SECCIÓN DE event_handlers ---
    self.set_event_handler('x-actualizar_form_activo', self.actualizar_form_activo)

    #--- IN/VISIBILIDAD Y DES/HABILITACIÓN DE COMPONENTES ---
    self.content_panel.visible = False #Es necesario dejar este content_panel, pues de no hacerlo sucede un bug: inicia el form mostrando "DRAG A COLUMN PANEL HERE" y si se deja pero invisible, pierde la propiedad de ser "clicable" dejándolo inservible para siempre.

  # --- SECCIÓN DE FUNCIONES DERIVADAS DE UN 'raise_event' EN FORMS HIJOS ---
  def actualizar_form_activo(self, datos, **event_args):
    if datos['clave_form'] == 'CALIDAD':
      self.abrir_form(CALIDAD(datos))
    elif datos['clave_form'] == 'CALIDAD_CONTROLDOCUMENTOS':
      self.abrir_form(CALIDAD_CONTROLDOCUMENTOS(datos))
    elif datos['clave_form'] == 'CALIDAD_CONTROLDOCUMENTOS_DOCUMENTOS_EXISTENTES':
      self.abrir_form(CALIDAD_CONTROLDOCUMENTOS_DOCUMENTOS_EXISTENTES(datos))
    elif datos['clave_form'] == 'CALIDAD_CONTROLDOCUMENTOS_HISTORIAL':
      self.abrir_form(CALIDAD_CONTROLDOCUMENTOS_HISTORIAL(datos))
    elif datos['clave_form'] == 'CALIDAD_CONTROLDOCUMENTOS_NUEVO_DOCUMENTO':
      self.abrir_form(CALIDAD_CONTROLDOCUMENTOS_NUEVO_DOCUMENTO(datos))
    elif datos['clave_form'] == 'CALIDAD_CONTROLDOCUMENTOS_VISOR_GOOGLE_APP':
      self.abrir_form(CALIDAD_CONTROLDOCUMENTOS_VISOR_GOOGLE_APP(datos))

  # --- SECCIÓN DE FUNCIONES USADAS POR DIFERENTES COMPONENTES DEL PROGRAMA ---
  def abrir_form(self, form_de_interes):
    try: #Se utiliza un try porque la primera vez que se abre el form RECUERSOS_HUMANOS no tiene ningún form hijo cargado, entonces levantará un error.
      self.form_activo.remove_from_parent()
    except: #no se necesita para manejar el error, pero el 'except' es obligado a estar cuando se usa un try. ¡NO BORRAR!
      pass
    self.form_activo = form_de_interes
    self.add_component(self.form_activo)

  def link_nav_calidad_click(self, **event_args):
    self.datos['clave_form'] = "CALIDAD"
    self.actualizar_form_activo(self.datos)

