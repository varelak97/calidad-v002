from ._anvil_designer import CALIDAD_CONTROLDOCUMENTOS_NUEVO_DOCUMENTOTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime, timedelta
from time import sleep

class CALIDAD_CONTROLDOCUMENTOS_NUEVO_DOCUMENTO(CALIDAD_CONTROLDOCUMENTOS_NUEVO_DOCUMENTOTemplate):
  #datos = {}
  datos = {
    "id_usuario_erp":7
  }
  background_task_google_script = None
  componentes_deshabilitables = []
  
  def __init__(self, **properties):#def __init__(self, datos, **properties):
    self.init_components(**properties)
    #self.datos = datos
    self.componentes_deshabilitables = [
      self.button_volver,
      self.drop_down_nivel,
      self.drop_down_documento_base,
      self.text_area_titulo,
      self.drop_down_tipo_archivo,
      self.drop_down_tipo_documento,
      self.drop_down_area,
      self.drop_down_consecutivo,
      self.drop_down_revision,
      self.button_generar_documento
    ]
    self.repeating_panel_creadores.items = []
    self.repeating_panel_revisores.items = []
    self.repeating_panel_validadores.items = []
    
    self.drop_down_tipo_documento.items = anvil.server.call('obtener_lista_tipos_documentos')
    if len(self.drop_down_tipo_archivo.items) == 1:
      self.drop_down_tipo_archivo.selected_value = self.drop_down_tipo_archivo.items[0]
    self.drop_down_area.items = anvil.server.call('obtener_lista_areas', self.datos['id_usuario_erp'])
    if len(self.drop_down_area.items) == 1:
      self.drop_down_area.selected_value = self.drop_down_area.items[0]
      self.drop_down_area_change()
    
    self.drop_down_nivel_change()
    self.drop_down_tipo_archivo_change()

  def habilitacion_general_componentes(self, bandera):
    for componente in self.componentes_deshabilitables:
      componente.enabled = bandera
      
  def button_volver_click(self, **event_args):
    self.content_panel.visible = False
    self.datos['clave_form'] = 'CALIDAD_CONTROLDOCUMENTOS'
    self.parent.raise_event('x-actualizar_form_activo', datos=self.datos)
    self.content_panel.visible = True

  def drop_down_nivel_change(self, **event_args):
    self.drop_down_tipo_archivo.selected_value = None
    self.drop_down_tipo_archivo_change()
    if self.drop_down_nivel.selected_value == None:
      self.drop_down_documento_base.placeholder = "-- PRIMERO ES NECESARIO ESPECIFICAR EL NIVEL DEL DOCUMENTO --"
      self.drop_down_documento_base.selected_value = None
      self.drop_down_documento_base.items =[]
    else:
      if "4" in self.drop_down_nivel.selected_value:
        self.drop_down_documento_base.placeholder = "NO APLICA"
        self.drop_down_documento_base.selected_value = None
        self.drop_down_documento_base.items = []
        self.drop_down_tipo_archivo.enabled = True
      else:
        self.drop_down_documento_base.items = anvil.server.call('obtener_documentos_base')
        if len(self.drop_down_documento_base.items) == 0:
          self.drop_down_documento_base.placeholder = " -- NO HAY DOCUMENTOS BASE DISPONIBLES --"
        else:
          self.drop_down_documento_base.placeholder = "-- ELEGIR --"
        self.drop_down_documento_base.selected_value = None
        self.drop_down_tipo_archivo.enabled = False
        
      
  def text_area_titulo_lost_focus(self, **event_args):
    self.text_area_titulo.text = str(self.text_area_titulo.text).upper()
    for texto_invalido in ("\n","  "):
      while texto_invalido in self.text_area_titulo.text:
        self.text_area_titulo.text = str(self.text_area_titulo.text).replace(texto_invalido," ")
    self.text_area_titulo.text = str(self.text_area_titulo.text).strip()

  def drop_down_area_change(self, **event_args):
    self.repeating_panel_creadores.items = []
    self.repeating_panel_revisores.items = []
    self.repeating_panel_validadores.items = []
    self.drop_down_propietario.placeholder = "-- SIN OPCIONES --"
    self.drop_down_propietario.selected_value = None
    self.drop_down_propietario.items = []
    
    if self.drop_down_area.selected_value == None:
      self.label_especificar_area.visible = True
    else:
      with Notification("Buscando equipo de trabajo correspondiente. Por favor espera...", title="CONSULTANDO BASE DE DATOS"):
        equipo_trabajo = anvil.server.call('obtener_nombres_equipo_trabajo_por_area', self.drop_down_area.selected_value)
      self.repeating_panel_creadores.items = equipo_trabajo['creadores']
      self.repeating_panel_revisores.items = equipo_trabajo['revisores']
      self.repeating_panel_validadores.items = equipo_trabajo['validadores']
      self.label_especificar_area.visible = False
      self.drop_down_propietario.items = sorted([item['integrante'] for item in self.repeating_panel_validadores.items])
      self.drop_down_propietario.placeholder = "-- ELEGIR --"
      if len(self.drop_down_propietario.items) == 1:
        self.drop_down_propietario.selected_value = self.drop_down_propietario.items[0]
      
  def button_generar_documento_click(self, **event_args):
    error = ""
    if self.drop_down_area.selected_value == None:
      error += "\n•Área."
    if self.drop_down_nivel.selected_value == None:
      error += "\n•Nivel."
    if self.drop_down_area.selected_value != None and "4" not in self.drop_down_nivel.selected_value and self.drop_down_nivel.selected_value != None and self.drop_down_documento_base.selected_value == None:
      error += "\n•Documento base."
    if len(self.repeating_panel_creadores.items) == 0:
      error += "\n•Por lo menos 1 creador."
    if len(self.repeating_panel_revisores.items) == 0:
      error += "\n•Por lo menos 1 revisor."
    if len(self.repeating_panel_validadores.items) == 0:
      error += "\n•Por lo menos 1 validador."
    if self.drop_down_propietario.selected_value == None:
      error += "\n•Propietario."
    if self.drop_down_tipo_documento.selected_value == None:
      error += "\n•Tipo de documento."
    if self.drop_down_tipo_archivo.selected_value == None:
      error += "\n•Tipo de archivo."
    if len(self.text_area_titulo.text) == 0:
      error += "\n•Título."
    """if self.drop_down_consecutivo.selected_value == None:
      error += "\n•Consecutivo."""
    if self.drop_down_revision.selected_value == None:
      error += "\n•Revisión."
    
    if len(error) > 0:
      error = f"Es necesario especificar la siguiente información:{error}"
    
    advertencia = ""
    if self.drop_down_agregar_creador.selected_value != None:
      advertencia += f"\n•El empleado {self.drop_down_agregar_creador.selected_value} fue elegido como \"CREADOR\" pero no se presionó el botón \"(+)\" para oficialmente añadirlo a la lista de creadores."
    if self.drop_down_agregar_revisor.selected_value != None:
      advertencia += f"\n•El empleado {self.drop_down_agregar_revisor.selected_value} fue elegido como \"REVISOR\" pero no se presionó el botón \"(+)\" para oficialmente añadirlo a la lista de revisores."
    if self.drop_down_agregar_validador.selected_value != None:
      advertencia += f"\n•El empleado {self.drop_down_agregar_validador.selected_value} fue elegido como \"validador\" pero no se presionó el botón \"(+)\" para oficialmente añadirlo a la lista de validadores."
    if len(advertencia) > 0:
      advertencia = f"¡ADVERTENCIA!:{advertencia}"
    
    if len(error) > 0:
      if len(advertencia) > 0:
        error += "\n\n" + advertencia
        ban_large = True
      else:
        ban_large = False
      alert(
        content = error,
        title = "FALTA INFORMACIÓN",
        large = ban_large
      )
    else:
      if len(advertencia) == 0:
        ban_continuar = True
      else:
        ban_continuar = confirm(
          content = advertencia + "\n\nSi procedes, se descartará(n) dicha(s) persona(s). ¿Deseas continuar?",
          title = "CONFIRMACIÓN REQUERIDA",
          buttons = [
            ("Sí. Procederé sin añadir.", True),
            ("No. Regresaré para añadir.", False)
          ],
          large = True,
          dismissible = False
        )
      if ban_continuar:
        self.content_panel.visible = False
        codigo = anvil.server.call('obtener_codigo_tipo_documento', self.drop_down_tipo_documento.selected_value)
        dicc_renglon_area = anvil.server.call('obtener_codigo_y_contadores_area', self.drop_down_area.selected_value)
        codigo += f"-{dicc_renglon_area['codigo']}-"
        consecutivo = dicc_renglon_area['contador_'+codigo[0:3]] + 1
        codigo += f"{'0' * (3 - len(str(consecutivo)))}{consecutivo}"
        #codigo += f"-{dicc_renglon_area['codigo']}-{self.drop_down_consecutivo.selected_value}" #Línea temporalmente usada para que Ada pueda subir documentos con consecutivos que no comienzan en "001"
        #alert(codigo) #LÍNEA PARA PRUEBAS
        
        self.datos['columna_contador'] = f"contador_{codigo[0:3]}"
        self.datos['consecutivo'] = consecutivo
        self.datos['nombre_area'] = self.drop_down_area.selected_value

        #ban_continuar_2 = anvil.server.call('comprobacion_codigo_no_repetido',codigo) #habilitar si operadores pueden ingresar consecutivo manualmente
        ban_continuar_2 = True
        if not ban_continuar_2:
          Notification(
            message = f"El código '{codigo}' ya fue generado anteriormente para otro documento.",
            title = "ACCIÓN DENEGADA",
            style='danger',
            timeout = 4
          ).show()
        else:
          self.datos.update(
            {
              "nivel": int(str(self.drop_down_nivel.selected_value).split('.')[0]),
              "nombre_documento_base": self.drop_down_documento_base.selected_value,
              "titulo": self.text_area_titulo.text,
              "codigo": codigo,
              "creadores": [item['integrante'] for item in self.repeating_panel_creadores.items],
              "revisores": [item['integrante'] for item in self.repeating_panel_revisores.items],
              "validadores": [item['integrante'] for item in self.repeating_panel_validadores.items],
              "numero_empleado_propietario": int(str(self.drop_down_propietario.selected_value).split('(')[1][0:-1]),
              "id_usuario_registrador": self.datos['id_usuario_erp'],
              "revision": self.drop_down_revision.selected_value #Línea temporalmente usada para que Ada pueda subir documentos con revisión que no comienzan en "00",
            }
          )
          self.datos["nombre_completo"] = f"{self.datos['codigo']} R{self.datos['revision']} {self.datos['titulo']}"
          self.datos["tipo_app"] = self.drop_down_tipo_archivo.selected_value
          if self.datos["tipo_app"] == "HOJA DE CÁLCULO" and self.datos['nivel'] == 4:
            self.datos["cantidad_hojas"] = self.text_box_cantidad_de_hojas.text
          self.datos["marca_temporal"] = datetime.now()
          
          for k,v in self.datos.items():
            print(k,":",v)
          
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
          #print(f"Respuesta = {respuesta}")
          if respuesta['exito_generacion_documento']:
            Notification(f"El documento {self.datos['codigo']} ha sido generado satisfactoriamente.", title="¡ÉXITO!", style='success',timeout=4).show()
            with Notification("Enviando correo electrónico de notificación al equipo de trabajo asignado. Por favor espera...", title = "NOTIFICACIÓN POR CORREO ELECTRÓNICO"):
              respuesta_envio_email = anvil.server.call(
                'enviar_email_notificacion',
                {
                  'id_registro_documento': respuesta['id_registro_documento'],
                  'operacion': 'creación'
                }
              )
              if not respuesta_envio_email[0]:
                empleados_creadores = ""
                for creador in self.datos['creadores']:
                  empleados_creadores += f'\n•{creador}'
                alert(
                  content = f"El documento {self.datos['nombre_completo']} fue generado satisfactoriamente, pero no fue posible enviar su respectiva notificación por correo electrónico al equipo de trabajo.\n\n{respuesta_envio_email[1]}\n\nPor favor informa a la(s) siguiente(s) persona(s) que la creación del documento ya ha sido realizada y puede(n) comenzar a trabajar en él:{empleados_creadores}",
                  title = "ERROR DURANTE ENVÍO DE NOTIFICACIÓN",
                  large=True,
                  dismissible=False
                )
              else:
                Notification("Notificación a equipo de trabajo enviada por correo electrónico", title="¡ÉXITO!", style='success').show()
                sleep(2)
            Notification("Por favor espera...", title="REDIRIGIENDO")
            self.datos = {
              'id_usuario_erp': self.datos['id_usuario_erp'],
              'clave_form': 'CALIDAD_CONTROLDOCUMENTOS_VISOR_GOOGLE_APP',
              'id_registro_documento': respuesta['id_registro_documento']
            }
            self.parent.raise_event('x-actualizar_form_activo', datos=self.datos)
          else:
            alert(
              content = respuesta['error'] + f"\n\nConfirma que tu dispositivo (PC, laptop o tablet) esté conectado a una red con acceso estable a internet e inténtalo nuevamente. Si el problema persiste, contacta al departamento de Sistemas.",
              title = "OCURRIÓ UN ERROR",
              dismissible=False
            )
    self.content_panel.visible = True

  def drop_down_tipo_archivo_change(self, **event_args):
    if self.drop_down_tipo_archivo.selected_value == "HOJA DE CÁLCULO":
      self.column_panel_cantidad_de_hojas.visible = True
    else:
      self.column_panel_cantidad_de_hojas.visible = False

  def text_box_cantidad_de_hojas_lost_focus(self, **event_args):
    if self.text_box_cantidad_de_hojas.text == None or int(self.text_box_cantidad_de_hojas.text) < 1:
      self.text_box_cantidad_de_hojas.text = 1
      Notification(
        message="La cantidad de hojas para un documento en Google Sheets debe ser por lo menos '1'.",
        title="ENTRADA INVÁLIDA",
        style="danger",
        timeout=3
      ).show()
    else:
      self.text_box_cantidad_de_hojas.text = int(self.text_box_cantidad_de_hojas.text)

  def drop_down_documento_base_change(self, **event_args):
    if self.drop_down_nivel.selected_value not in (None,"4. Formatos"):
      id_registro_documento_base = anvil.server.call('obtener_id_registro', self.drop_down_documento_base.selected_value)
      tipo_archivo = anvil.server.call('obtener_renglon_documento', id_registro_documento_base)['tipo_app']
      self.drop_down_tipo_archivo.selected_value = tipo_archivo

  def button_actualizar_contadores_click(self, **event_args):
    #inserar boton con el nombre: button_actualizar_contadores
    #insertar textbox con el nombre: text_box_pref
    terminaciones = ["MDG","MOP","PRO","PDC","DIF","INS","ADM","AVI","FOR","TAR","LAY","REG","ETI","MAT","PCO","PIN","TIN"]
    nuevas_terminaciones = []
    with Notification("Buscando ultimo numero generado de cada codigo, espere...", title="BUSCANDO.", style="notification"):
      for item in terminaciones:
        item = f"{item}-{self.text_box_pref.text}"
        nuevas_terminaciones.append(item)
      registros_documentos = anvil.server.call('obtener_documentos_registrados')
      encontrados = []
      for registro in registros_documentos:
        for terminacion in nuevas_terminaciones:
          if terminacion in registro['codigo']:
            encontrados.append(registro['codigo'])
      contadores = {}
      for pref in nuevas_terminaciones:
        array = [int(item.split("-")[2]) for item in encontrados if pref in item]
        contadores[pref] = max(array) if len(array) > 0 else 0
    with Notification("Actualizando contadores, espere...", title="ACTUALIZANDO.", style="notification"):
      anvil.server.call('actualizar_contadores', contadores, nuevas_terminaciones, self.text_box_pref.text)
    Notification("Registro actualizado con éxito.", title="HECHO!", style="success").show(3)

  @handle("drop_down_revision", "change")
  def drop_down_revision_change(self, **event_args):
    """This method is called when an item is selected"""
    pass
    
    
    
