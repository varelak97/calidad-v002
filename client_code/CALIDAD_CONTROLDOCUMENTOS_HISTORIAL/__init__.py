from ._anvil_designer import CALIDAD_CONTROLDOCUMENTOS_HISTORIALTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class CALIDAD_CONTROLDOCUMENTOS_HISTORIAL(CALIDAD_CONTROLDOCUMENTOS_HISTORIALTemplate):
  datos = {}
  def __init__(self, datos, **properties):
    self.init_components(**properties)
    self.datos = datos
    historial = anvil.server.call('obtener_historial_documento', datos['id_registro_documento'])
    self.label_nombre_documento.text = f"HISTORIAL DE {historial[0]['nombre_completo'][0:15]}"
    items = []
    dicc_item = {}
    for item in historial:
      dicc_inicial = dict(item)
      dicc_item = {}
      dicc_item['marca_temporal'] = str(dicc_inicial['marca_temporal'])[0:19]
      dicc_item['operacion'] = dicc_inicial['operacion']
      nombre_completo_empleado, numero_empleado = anvil.server.call('obtener_info_empleado', dicc_inicial['id_usuario_registrador'])
      dicc_item['nombre_completo_empleado'] = nombre_completo_empleado + f" ({numero_empleado})"
      dicc_item['nombre_completo_documento'] = dicc_inicial['nombre_completo']
      dicc_item['status'] = dicc_inicial['status']
      dicc_item['tipo_archivo'] = dicc_inicial['tipo_app']
      nombre_completo_empleado, numero_empleado = anvil.server.call('obtener_info_empleado', dicc_inicial['id_usuario_propietario'])
      dicc_item['propietario'] = nombre_completo_empleado + f" ({numero_empleado})"
      dicc_item['comentarios_renglon'] = dicc_inicial['comentarios_renglon']
      dicc_item['documento_base'] = anvil.server.call('obtener_renglon_documento', dicc_inicial['id_documento_base'])['nombre_completo']
      equipo_trabajo_id_usuarios_erp = {
        'creadores': dicc_inicial['creadores'],
        'revisores': dicc_inicial['revisores'],
        'validadores': dicc_inicial['validadores'],
      }
      equipo_trabajo_nombres = anvil.server.call('obtener_nombres_equipo_de_trabajo', equipo_trabajo_id_usuarios_erp)
      for sub_equipo in ('creadores', 'revisores', 'validadores'):
        dicc_item[sub_equipo] = ""
        for empleado in equipo_trabajo_nombres[sub_equipo]:
          dicc_item[sub_equipo] += empleado + "\n"
        dicc_item[sub_equipo] = dicc_item[sub_equipo][0:-1]  
      items.append(dicc_item)
    self.repeating_panel_historial_documento.items = items

  def button_volver_click(self, **event_args):
    self.datos['clave_form'] = 'CALIDAD_CONTROLDOCUMENTOS_DOCUMENTOS_EXISTENTES'
    self.parent.raise_event('x-actualizar_form_activo', datos=self.datos)

  