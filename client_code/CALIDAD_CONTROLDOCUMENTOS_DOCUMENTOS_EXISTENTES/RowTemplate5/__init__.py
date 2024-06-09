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
      ids_equipo = anvil.server.call('obtener_ids_equipo_de_documento', self.label_nombre_documento.text)
      if id_usuario_erp in ids_equipo:
        botones.append(("NUEVA REVISIÓN", "CALIDAD_CONTROLDOCUMENTOS_NUEVO_DOCUMENTO"))
        pass
      
    evento = alert(
      content = "",
      title = "ELIGE UNA OPERACIÓN",
      buttons = botones
    )
    if evento != None:
      confirmacion = alert(
        content = "¿Confirma que desea generar una nueva revisión de este documento?",
        buttons=(("SI", True),("No", False))
      )
      if confirmacion:
        self.parent.parent.parent.parent.visible = False
        datos = {
            'id_usuario_erp': id_usuario_erp,
            'clave_form': evento,
            'id_registro_documento': anvil.server.call('obtener_id_registro', self.label_nombre_documento.text)
          }
        """self.parent.parent.parent.parent.parent.parent.raise_event('x-actualizar_form_activo', datos=datos)
        self.parent.parent.parent.parent.visible = True"""
        with Notification("Trabajando en la generación del documento. Este proceso tomará algo de tiempo; por favor espera...", title="PROCESANDO PETICIÓN"):
            self.background_task_google_script = anvil.server.call('lanzar_background_google_script', 'generacion_documento', self.datos)
            tiempo_inicio = datetime.now()
            tiempo_final = tiempo_inicio + timedelta(minutes=1, seconds=30)
            ban_timeout = False
            while self.background_task_google_script.is_running():
              if datetime.now() >= tiempo_final:
                ban_timeout = True
                break
              elif datetime.now() >= (tiempo_inicio + timedelta(seconds=2)):
                respuesta = self.background_task_google_script.get_state()['respuesta']
            #print(f"{self.background_task_google_script.get_error()}")
            respuesta = self.background_task_google_script.get_state()['respuesta']
          sleep(1)
          print(f"Respuesta = {respuesta}")
          if respuesta['exito_generacion_documento']:
            Notification(f"El documento {self.datos['codigo']} ha sido generado satisfactoriamente.", title="¡ÉXITO!", style='success',timeout=4).show()