import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import json
import requests
from time import sleep

global url_google_script
#url_google_script = "https://script.google.com/macros/s/AKfycbyDThc91c9r9hXynjW3NKZAkH-cS1jMyY0W1TPchwEAd-eDKGRFqEuuIwNAzvEBL3A/exec"
#url_google_script = "https://script.google.com/macros/s/AKfycbxFX3NZD4B7sw42xGBorO_yjl-EQj-sDjpXtQchpmKnqw-P54mKgJTpdk4cEmdk_xc/exec" #VERSION ANTERIOR SIN NUEVA REVISION
url_google_script = "https://script.google.com/macros/s/AKfycby9wS3-4Yvy__R-mQPwQyiSYgxHtIv8A3qCmjUMOwFkaG8VLydX7IVHLv-ijKAi0OI/exec"

#--- SECCIÓN DE FUNCIONES PARA FORMULARIO DE MENÚ PRINCIPAL ---

@anvil.server.callable
def aux():
  
  """
  dicc_areas = {str(r['id_registro_area']):r['area'] for r in app_tables.calidad_controldocumentos_areas.search()}
  
  print("AREAS")
  for k,v in dicc_areas.items():
    print(f"{k}: {v}")
  """  
  dicc_empleados = {str(r['id_registro_empleado']):r['nombre_completo'] for r in app_tables.rh_empleados_infobase.search()}
  
  print("EMPLEADOS")
  for k,v in dicc_empleados.items():
    print(f"{k}: {v}")
  
  dicc_usuarios = {str(r['id_registro_usuario']):dicc_empleados[str(r['id_registro_empleado'])] for r in app_tables.sistemas_usuarios_erp_registro.search()}
  #"""
  print("USUARIOS")
  for k,v in dicc_usuarios.items():
    print(f"{k}: {v}")
  #"""

@anvil.server.callable
def aux2():
  for r in app_tables.calidad_controldocumentos_equipotrabajo.search():
    if 15 in r['revisores']:
      r['revisores'] = [7, 15]
      
  for r in app_tables.calidad_controldocumentos_registrodocumentos.search(registro_principal=True):
    if 15 in r['revisores']:
      r['revisores'] = [7, 15]
  
  
@anvil.server.callable
def obtener_id_usuario_erp_desde_numero_empleado(numero_empleado):
  renglon_empleado = app_tables.rh_empleados_infobase.get(numero_empleado=numero_empleado, registro_principal=True)
  renglon_usuario = app_tables.sistemas_usuarios_erp_registro.get(id_registro_empleado=renglon_empleado['id_registro_empleado'], registro_principal=True)
  id_usuario_erp = renglon_usuario['id_registro_usuario']
  return id_usuario_erp
  
@anvil.server.callable
def obtener_lista_id_validadores():    
  lista_id_validadores =  [id_validador for r in app_tables.calidad_controldocumentos_equipotrabajo.search() for id_validador in r['validadores']]
  lista_id_validadores = list(set(lista_id_validadores))
  return lista_id_validadores

@anvil.server.callable
def verificacion_pertenencia_a_equipo(id_usuario_erp):
	bandera_retorno = False
	for sub_equipo in ("creadores","revisores","validadores"):
		ids_integrantes = [id_integrante for r in app_tables.calidad_controldocumentos_equipotrabajo.search() for id_integrante in r[sub_equipo]]
		if id_usuario_erp in ids_integrantes:
			bandera_retorno = True
			break
	return bandera_retorno

#--- SECCIÓN DE FUNCIONES PARA FORMULARIO DE GENERACIÓN DE NUEVO DOCUMENTO ---
@anvil.server.callable
def obtener_documentos_base():
  documentos_base = sorted([r['nombre_completo'] for r in app_tables.calidad_controldocumentos_registrodocumentos.search(nivel=4, status="Liberado", registro_principal=True, registro_activo=True)])
  return documentos_base
  
@anvil.server.callable
def obtener_lista_tipos_documentos():
  return sorted([r['tipo'] for r in app_tables.calidad_controldocumentos_tipodocumentos.search()])

@anvil.server.callable
def obtener_lista_areas(id_usuario_erp):
  ids_areas = [r['id_registro_area'] for r in app_tables.calidad_controldocumentos_equipotrabajo.search(registro_principal=True) if id_usuario_erp in r['creadores'] or id_usuario_erp in r['revisores'] or id_usuario_erp in r['validadores']]
  areas = sorted([r['area'] for r in app_tables.calidad_controldocumentos_areas.search() if r['id_registro_area'] in ids_areas])
  return areas

@anvil.server.callable
def obtener_codigo_tipo_documento(tipo):
  return app_tables.calidad_controldocumentos_tipodocumentos.get(tipo=tipo)['codigo']

@anvil.server.callable
def obtener_codigo_y_contadores_area(area):
  return app_tables.calidad_controldocumentos_areas.get(area=area)

@anvil.server.callable
def obtener_nombres_equipo_trabajo_por_area(area):
  id_registro_area = app_tables.calidad_controldocumentos_areas.get(area=area)['id_registro_area']
  renglon_equipo_trabajo = app_tables.calidad_controldocumentos_equipotrabajo.get(id_registro_area=id_registro_area, registro_principal=True)
  equipo_trabajo = {}
  for sub_equipo in ['creadores','revisores','validadores']:
    lista_id_registro_usuario_sub_equipo = renglon_equipo_trabajo[sub_equipo]
    lista_id_registro_empleado_sub_equipo = []
    for id_registro_usuario in lista_id_registro_usuario_sub_equipo:
      lista_id_registro_empleado_sub_equipo.append(app_tables.sistemas_usuarios_erp_registro.get(id_registro_usuario=id_registro_usuario, registro_principal=True)['id_registro_empleado'])
    info_sub_equipo = []
    for id_registro_empleado in lista_id_registro_empleado_sub_equipo:
      renglon_empleado = app_tables.rh_empleados_infobase.get(id_registro_empleado=id_registro_empleado, registro_principal=True)
      info_sub_equipo.append({'integrante':f"{renglon_empleado['nombre_completo']} ({renglon_empleado['numero_empleado']})"})
    equipo_trabajo[sub_equipo] = sorted(info_sub_equipo, key=lambda d:d['integrante'])
    
  return equipo_trabajo

#--- SECCIÓN DE FUNCIONES LLAMADAS DESDE OTRAS FUNCIONES DE ESTE SERVER MODULE ---
@anvil.server.callable
def tipo_google_app(tipo):
  dicc = {
    'PROCESADOR DE TEXTO': 'document',
    'HOJA DE CÁLCULO': 'spreadsheets',
    'PRESENTACIÓN': 'presentation'
  }
  return dicc[tipo]

@anvil.server.callable
def obtener_emails_editores(id_registro_documento):
  renglon_documento = app_tables.calidad_controldocumentos_registrodocumentos.get(id_registro_documento=id_registro_documento, registro_principal = True)
  emails_editores = ""
  for editor in renglon_documento['creadores']:
    renglon_usuario_erp = app_tables.sistemas_usuarios_erp_registro.get(id_registro_usuario=editor, registro_principal=True)
    renglon_empleado = app_tables.rh_empleados_infobase.get(id_registro_empleado=renglon_usuario_erp['id_registro_empleado'], registro_principal=True)
    emails_editores += renglon_empleado['email_laboral'] + ','
  return emails_editores[0:-1]

@anvil.server.callable
def obtener_emails_lectores(emails_editores):
  emails_lectores = ""
  for r in app_tables.rh_empleados_infobase.search(registro_principal=True):
    if r['email_laboral'] != None and str(r['email_laboral']) not in emails_editores and "@ensel.org" not in str(r['email_laboral']):
      emails_lectores += str(r['email_laboral']) + ','
  return emails_lectores[0:-1]

@anvil.server.callable
def comprobacion_codigo_no_repetido(codigo):
  if len(app_tables.calidad_controldocumentos_registrodocumentos.search(codigo=codigo,registro_principal=True)) == 0:
    return True
  else:
    return False

@anvil.server.callable
def lanzar_background_google_script(clave_subscript, datos):
  if clave_subscript == 'generacion_documento':
    return anvil.server.launch_background_task('generar_documento', datos)
  elif clave_subscript == 'envio_a_revision_documento':
    return anvil.server.launch_background_task('enviar_documento_a_revision', datos)
  elif clave_subscript == 'rechazo_documento':
    return anvil.server.launch_background_task('rechazar_documento', datos)
  elif clave_subscript == 'liberacion_documento':
    return anvil.server.launch_background_task('liberar_documento', datos)
  elif clave_subscript == 'generar_nueva_revision':
    return anvil.server.launch_background_task('generar_nueva_revision', datos)


#--- SECCIÓN FUNCIONES DE FLUJO DE DOCUMENTOS ---
@anvil.server.background_task
def generar_documento(datos):
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':'1. Comenzó pero no terminó'}
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':f'datos:\n{datos}'}

  """
    id_renglon = max([r['id_renglon'] for r in app_tables.calidad_controldocumentos_registrodocumentos.search(registro_principal=True)]) + 1 if len(app_tables.calidad_controldocumentos_registrodocumentos.search()) > 0 else 1,
    id_registro_documento = max([r['id_registro_documento'] for r in app_tables.calidad_controldocumentos_registrodocumentos.search(registro_principal=True)]) + 1 if len(app_tables.calidad_controldocumentos_registrodocumentos.search()) > 0 else 1,
  	id_version_documento = 1,
    registro_principal = True,
    registro_activo = True,
    nivel = datos['nivel'],
    codigo = datos['codigo'],
  	#revision = 0,
    revision=int(datos['revision']), #Línea temporalmente usada para que Ada pueda subir documentos con revisión que no comienzan en "00"
    titulo = datos['titulo'],
  	nombre_completo = datos['nombre_completo'],
  	fecha_emision = None,
    tipo_app = datos['tipo_app'],
    status = "En creación",
    id_usuario_propietario = obtener_id_usuario_erp_desde_numero_empleado(datos['numero_empleado_propietario']),
    operacion = "Creación del documento",
    id_usuario_registrador = datos['id_usuario_registrador'],
    marca_temporal = datos['marca_temporal']
  
  id_renglon = max([r['id_renglon'] for r in app_tables.calidad_controldocumentos_registrodocumentos.search(registro_principal=True)]) + 1 if len(app_tables.calidad_controldocumentos_registrodocumentos.search()) > 0 else 1
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':f'id_renglon:\n{id_renglon}'}
  id_registro_documento = max([r['id_registro_documento'] for r in app_tables.calidad_controldocumentos_registrodocumentos.search(registro_principal=True)]) + 1 if len(app_tables.calidad_controldocumentos_registrodocumentos.search()) > 0 else 1
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':f'id_registro_documento:\n{id_registro_documento}'}
  id_version_documento = 1
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':f'id_version_documento:\n{id_version_documento}'}
  registro_principal = True
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':f'registro_principal:\n{registro_principal}'}
  registro_activo = True
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':f'registro_activo:\n{registro_activo}'}
  nivel = datos['nivel']
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':f'nivel:\n{nivel}'}
  codigo = datos['codigo']
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':f'codigo:\n{codigo}'}
  #revision = 0,
  revision=int(datos['revision']) #Línea temporalmente usada para que Ada pueda subir documentos con revisión que no comienzan en "00"
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':f'revision:\n{revision}'}
  titulo = datos['titulo']
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':f'titulo:\n{titulo}'}
  nombre_completo = datos['nombre_completo']
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':f'nombre_completo:\n{nombre_completo}'}
  fecha_emision = None
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':f'fecha_emision:\n{fecha_emision}'}
  tipo_app = datos['tipo_app']
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':f'tipo_app:\n{tipo_app}'}
  status = "En creación"
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':f'status:\n{status}'}
  #id_usuario_propietario = obtener_id_usuario_erp_desde_numero_empleado(datos['numero_empleado_propietario'])
  id_usuario_propietario = 18
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':f'id_usuario_propietario:\n{id_usuario_propietario}'}
  operacion = "Creación del documento"
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':f'operacion:\n{operacion}'}
  id_usuario_registrador = datos['id_usuario_registrador']
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':f'id_usuario_registrador:\n{id_usuario_registrador}'}
  marca_temporal = datos['marca_temporal']
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':f'marca_temporal:\n{marca_temporal}'}
  """
  
  nuevo_renglon_registro_documento = app_tables.calidad_controldocumentos_registrodocumentos.add_row(
    id_renglon = max([r['id_renglon'] for r in app_tables.calidad_controldocumentos_registrodocumentos.search(registro_principal=True)]) + 1 if len(app_tables.calidad_controldocumentos_registrodocumentos.search()) > 0 else 1,
    id_registro_documento = max([r['id_registro_documento'] for r in app_tables.calidad_controldocumentos_registrodocumentos.search(registro_principal=True)]) + 1 if len(app_tables.calidad_controldocumentos_registrodocumentos.search()) > 0 else 1,
  	id_version_documento = 1,
    registro_principal = True,
    registro_activo = True,
    nivel = datos['nivel'],
    codigo = datos['codigo'],
  	#revision = 0,
    revision=int(datos['revision']), #Línea temporalmente usada para que Ada pueda subir documentos con revisión que no comienzan en "00"
    titulo = datos['titulo'],
  	nombre_completo = datos['nombre_completo'],
  	fecha_emision = None,
    tipo_app = datos['tipo_app'],
    status = "En creación",
    id_usuario_propietario = obtener_id_usuario_erp_desde_numero_empleado(datos['numero_empleado_propietario']),
    operacion = "Creación del documento",
    id_usuario_registrador = datos['id_usuario_registrador'],
    marca_temporal = datos['marca_temporal']
  )
  
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':'2. Generé renglón nuevo'}
  for sub_equipo in ('creadores','revisores','validadores'):
    id_usuario_integrantes = []
    for integrante in datos[sub_equipo]:
      numero_empleado = int(str(integrante).split()[-1].replace('(','').replace(')',''))
      renglon_registro_empleado = app_tables.rh_empleados_infobase.get(numero_empleado=numero_empleado, registro_principal=True)
      id_registro_empleado = renglon_registro_empleado['id_registro_empleado']
      id_usuario_integrantes.append(app_tables.sistemas_usuarios_erp_registro.get(id_registro_empleado=id_registro_empleado, registro_principal=True)['id_registro_usuario'])
    nuevo_renglon_registro_documento[sub_equipo] = id_usuario_integrantes.copy()
  documento_base = datos['nombre_documento_base']
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':'3. Obtuve integrantes del equipo.'}
  
  if documento_base != None:
    documento_base = datos['nombre_documento_base'].split()
    renglon_documento_base = app_tables.calidad_controldocumentos_registrodocumentos.get(codigo=documento_base[0],status="Liberado",registro_principal=True)
    nuevo_renglon_registro_documento['id_documento_base'] = renglon_documento_base['id_registro_documento']
    anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':'3.1 actualicé id_documento_base'}
  
  
  dicc_google_script = {
    'id_registro_documento': nuevo_renglon_registro_documento['id_registro_documento'],
    'id_version_documento': nuevo_renglon_registro_documento['id_version_documento'],
    'titulo': nuevo_renglon_registro_documento['titulo'],
    'codigo_documento': nuevo_renglon_registro_documento['codigo'],
    'revision_documento': nuevo_renglon_registro_documento['revision'],
    'codigo_formato': nuevo_renglon_registro_documento['codigo'] if documento_base == None else renglon_documento_base['codigo'],
    'revision_formato': nuevo_renglon_registro_documento['revision'] if documento_base == None else renglon_documento_base['revision'],
    'fecha_formato': None if documento_base == None else str(renglon_documento_base['fecha_emision']),
    'operacion': "creacion",
    'nombre_completo': nuevo_renglon_registro_documento['nombre_completo'],
    'tipo_app': tipo_google_app(datos['tipo_app']),
    'nivel': nuevo_renglon_registro_documento['nivel'],
    'id_google_doc_base': None if datos['nivel'] == 4 else renglon_documento_base['id_google']
  }
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':f'4. Llené primera parte de dicc_google_script {dicc_google_script}'}
  
  if datos['tipo_app'] == "HOJA DE CÁLCULO" and datos['nivel'] == 4:
    dicc_google_script['cantidad_hojas'] = datos['cantidad_hojas']
    anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':'4.1 indiqué cantidad de hojas para Sheets.'}
    
  dicc_google_script['emails_editores'] = obtener_emails_editores(nuevo_renglon_registro_documento['id_registro_documento'])
  dicc_google_script['emails_lectores'] = obtener_emails_lectores(dicc_google_script['emails_editores'])
  anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':'5. Asigné lista de emails de editores y lectores'}

  print(json.dumps(dicc_google_script, indent=4))
  
  respuesta = {} #Declarando antes del Try porque genera un error --> UnboundLocalError: local variable 'respuesta' referenced before assignment
  anvil.server.task_state['proceso'] = "Comunicando con Google Apps Scripts..."
  
  try:
    anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':'6. Llamando al script de Google'}
    nuevo_renglon_registro_documento['id_google'] = json.loads(requests.post(url_google_script, data=dicc_google_script).text)['id_doc']
  except Exception as Ex:
    #try / except para borrar la carpeta correspondiente en Google Drive.
    anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':'7.Falló el script de Google'}
    nuevo_renglon_registro_documento.delete()
    respuesta = {
      'exito_generacion_documento': False,
      'error': f"Tipo de error:\n{type(Ex)}\n\nMensaje de error:\n{Ex}"
    }
  else:
    """
    aux_codigo = datos['codigo'].split('-')
    codigo_tipo_documento = aux_codigo[0]
    codigo_area = aux_codigo[1]
    renglon_area = app_tables.calidad_controldocumentos_areas.get(codigo=codigo_area)
    renglon_area['contador_'+codigo_tipo_documento] += 1
    """
    anvil.server.task_state['respuesta'] = {'exito_generacion_documento': None, 'error':'8. Script de Google finalizado'}
    anvil.server.task_state['ban_finalizado'] = True
    respuesta = {
      'exito_generacion_documento': True,
      'id_registro_documento': nuevo_renglon_registro_documento['id_registro_documento']
    }
  finally:
    anvil.server.task_state['respuesta'] = respuesta
    sleep(2)

@anvil.server.background_task
def enviar_documento_a_revision(datos):
  anvil.server.task_state['respuesta'] = {'exito_envio_a_revision_documento': None, 'error':'Comenzó pero no terminó'}
  anterior_renglon_registro_documento = app_tables.calidad_controldocumentos_registrodocumentos.get(id_registro_documento=datos['id_registro_documento'], registro_principal=True)
  info_renglon_documento_actual = dict(anterior_renglon_registro_documento)
  nuevo_renglon_registro_documento = app_tables.calidad_controldocumentos_registrodocumentos.add_row(**info_renglon_documento_actual)
  nuevo_renglon_registro_documento['id_renglon'] = max([r['id_renglon'] for r in app_tables.calidad_controldocumentos_registrodocumentos.search(registro_principal=True)]) + 1
  nuevo_renglon_registro_documento['registro_principal'] = False
  nuevo_renglon_registro_documento['id_version_documento'] += 1
  nuevo_renglon_registro_documento['status'] = 'En revisión'
  nuevo_renglon_registro_documento['operacion'] = "Envío a revisión"
  nuevo_renglon_registro_documento['id_usuario_registrador'] = datos['id_usuario_registrador']
  nuevo_renglon_registro_documento['marca_temporal'] = datos['marca_temporal']
  nuevo_renglon_registro_documento['comentarios_renglon'] = None
  
  dicc_google_script = {
    'id_registro_documento': anterior_renglon_registro_documento['id_registro_documento'],
    'id_version_documento': anterior_renglon_registro_documento['id_version_documento'],
    'id_google': anterior_renglon_registro_documento['id_google'],
    'revision_documento': anterior_renglon_registro_documento['revision'],
    'tipo_app': tipo_google_app(anterior_renglon_registro_documento['tipo_app']),
    'operacion': 'revision',
    'emails_lectores': obtener_emails_lectores(""),
    'nombre_completo': nuevo_renglon_registro_documento['nombre_completo']
  }
  respuesta = {}
  anvil.server.task_state['respuesta'] = dicc_google_script#eliminaaaaaaaaaaaaaaaaaaaaa!!!!!!
  anvil.server.task_state['proceso'] = "Comunicando con Google Apps Scripts..."
  try:
    nuevo_renglon_registro_documento['id_google'] = json.loads(requests.post(url_google_script, data=dicc_google_script).text)['id_doc']
  except Exception as Ex:
    #try / except para borrar la carpeta correspondiente en Google Drive.
    nuevo_renglon_registro_documento.delete()
    respuesta = {
      'exito_envio_a_revision_documento': False,
      'error': f"Tipo de error:\n{type(Ex)}\n\nMensaje de error:\n{Ex}"
    }
    #respuesta = [False, f"Tipo de error:\n{type(Ex)}\n\nMensaje de error:\n{Ex}"]
  else:
    nuevo_renglon_registro_documento['registro_principal'] = True
    anterior_renglon_registro_documento.update(registro_principal=False)
    anvil.server.task_state['proceso'] = "¡Scipt de Google terminado!"
    anvil.server.task_state['ban_finalizado'] = True
    respuesta = {
      'exito_envio_a_revision_documento': True,
      'id_registro_documento': nuevo_renglon_registro_documento['id_registro_documento']
    }
    #respuesta = [True, nuevo_renglon_registro_documento['id_registro_documento']]
  finally:
    anvil.server.task_state['respuesta'] = respuesta
    sleep(2)
    #return respuesta 

@anvil.server.background_task
def generar_nueva_revision(datos):
  anvil.server.task_state['respuesta'] = {'exito_creacion_nueva_revision': None, 'error':'Comenzó pero no terminó generar nueva revision'}
  anterior_renglon_registro_documento = app_tables.calidad_controldocumentos_registrodocumentos.get(id_registro_documento=datos['id_registro_documento'], registro_principal=True)
  info_renglon_documento_actual = dict(anterior_renglon_registro_documento)
  nuevo_renglon_registro_documento = app_tables.calidad_controldocumentos_registrodocumentos.add_row(**info_renglon_documento_actual)
  nuevo_renglon_registro_documento['id_renglon'] = max([r['id_renglon'] for r in app_tables.calidad_controldocumentos_registrodocumentos.search(registro_principal=True)]) + 1
  nuevo_renglon_registro_documento['registro_principal'] = False
  #anvil.server.task_state['respuesta'] = {'exito_creacion_nueva_revision': None, 'error': "antes de id_version_documento = 1"}
  nuevo_renglon_registro_documento['id_version_documento'] = 1
  nuevo_renglon_registro_documento['revision'] += 1
  nuevo_renglon_registro_documento['status'] = 'En creación'
  nuevo_renglon_registro_documento['operacion'] = "Creación"
  #anvil.server.task_state['respuesta'] = {'exito_creacion_nueva_revision': None, 'error': "antes de id usuario registrador"}
  nuevo_renglon_registro_documento['id_usuario_registrador'] = datos['id_usuario_registrador']
  #anvil.server.task_state['respuesta'] = {'exito_creacion_nueva_revision': None, 'error': "despues de id usuario registrador"}
  nuevo_renglon_registro_documento['marca_temporal'] = datos['marca_temporal']
  """anvil.server.task_state['respuesta'] = {'exito_creacion_nueva_revision': None, 'error': "despues de marca temporal"}
  anvil.server.task_state['respuesta'] = {'exito_creacion_nueva_revision': None, 'error': "antes de comentarios"}"""
  nuevo_renglon_registro_documento['comentarios_renglon'] = None

  #anvil.server.task_state['respuesta'] = {'exito_creacion_nueva_revision': None, 'error': "antes de generar dicc"}

  dicc_google_script = {
    'id_registro_documento': anterior_renglon_registro_documento['id_registro_documento'],
    'id_version_documento': 1,
    'id_google': anterior_renglon_registro_documento['id_google'],
    'revision_documento': anterior_renglon_registro_documento['revision'],
    'fecha_documento': str(anterior_renglon_registro_documento['fecha_emision']),
    'tipo_app': tipo_google_app(anterior_renglon_registro_documento['tipo_app']),
    'operacion': 'nueva_revision',
    'emails_lectores': obtener_emails_lectores(""),
    'nombre_completo': nuevo_renglon_registro_documento['nombre_completo']
  }

  #anvil.server.task_state['respuesta'] = {'exito_creacion_nueva_revision': None, 'error': dicc_google_script} #borraaaaaaaaaaaaaaaaaaa!!!!!!!!!!!!

  respuesta = {}
  anvil.server.task_state['proceso'] = "Comunicando con Google Apps Scripts..."
  try:
    nuevo_renglon_registro_documento['id_google'] = json.loads(requests.post(url_google_script, data=dicc_google_script).text)['id_doc']
  except Exception as Ex:
    print("ocurrio una excepcion")
    #try / except para borrar la carpeta correspondiente en Google Drive.
    nuevo_renglon_registro_documento.delete()
    respuesta = {
      'exito_creacion_nueva_revision': False,
      'error': f"Tipo de error:\n{type(Ex)}\n\nMensaje de error:\n{Ex}"
    }
    #respuesta = [False, f"Tipo de error:\n{type(Ex)}\n\nMensaje de error:\n{Ex}"]
  else:
    nuevo_renglon_registro_documento['registro_principal'] = True
    nuevo_renglon_registro_documento['fecha_emision'] = None
    anterior_renglon_registro_documento.update(registro_principal=False)
    anvil.server.task_state['proceso'] = "¡Scipt de Google terminado!"
    anvil.server.task_state['ban_finalizado'] = True
    respuesta = {
      'exito_creacion_nueva_revision': True,
      'id_registro_documento': nuevo_renglon_registro_documento['id_registro_documento']
    }
    #respuesta = [True, nuevo_renglon_registro_documento['id_registro_documento']]
  finally:
    respuesta['error'] = dicc_google_script
    anvil.server.task_state['respuesta'] = respuesta
    sleep(2)
    #return respuesta



@anvil.server.background_task
def rechazar_documento(datos):
  anvil.server.task_state['respuesta'] = {'exito_rechazo_documento': None, 'error':'Comenzó pero no terminó'}
  anterior_renglon_registro_documento = app_tables.calidad_controldocumentos_registrodocumentos.get(id_registro_documento=datos['id_registro_documento'], registro_principal=True)
  info_renglon_documento_actual = dict(anterior_renglon_registro_documento)
  nuevo_renglon_registro_documento = app_tables.calidad_controldocumentos_registrodocumentos.add_row(**info_renglon_documento_actual)
  nuevo_renglon_registro_documento['id_renglon'] = max([r['id_renglon'] for r in app_tables.calidad_controldocumentos_registrodocumentos.search(registro_principal=True)]) + 1
  nuevo_renglon_registro_documento['registro_principal'] = False
  nuevo_renglon_registro_documento['status'] = 'Rechazado'
  nuevo_renglon_registro_documento['operacion'] = "Rechazo"
  nuevo_renglon_registro_documento['comentarios_renglon'] = datos['motivo_rechazo']
  nuevo_renglon_registro_documento['id_usuario_registrador'] = datos['id_usuario_registrador']
  nuevo_renglon_registro_documento['marca_temporal'] = datos['marca_temporal']

  dicc_google_script = {
    'id_registro_documento': nuevo_renglon_registro_documento['id_registro_documento'],
    'id_version_documento': nuevo_renglon_registro_documento['id_version_documento'],
    'id_google': nuevo_renglon_registro_documento['id_google'],
    'revision_documento': anterior_renglon_registro_documento['revision'],
    'tipo_app': tipo_google_app(anterior_renglon_registro_documento['tipo_app']),
    'operacion': 'rechazo',
    'nombre_completo': nuevo_renglon_registro_documento['nombre_completo'],
  }
  dicc_google_script['emails_editores'] = obtener_emails_editores(nuevo_renglon_registro_documento['id_registro_documento'])
  dicc_google_script['emails_lectores'] = obtener_emails_lectores(dicc_google_script['emails_editores'])
  respuesta = {}
  anvil.server.task_state['proceso'] = "Comunicando con Google Apps Scripts..."
  try:
    id_doc = json.loads(requests.post(url_google_script, data=dicc_google_script).text)['id_doc']
    if nuevo_renglon_registro_documento['tipo_app'] == "PRESENTACIÓN":
      nuevo_renglon_registro_documento['id_google'] = id_doc
  except Exception as Ex:
    #try / except para borrar la carpeta correspondiente en Google Drive.
    nuevo_renglon_registro_documento.delete()
    respuesta = {
      'exito_rechazo_documento': False,
      'error': f"Tipo de error:\n{type(Ex)}\n\nMensaje de error:\n{Ex}"
    }
  else:
    nuevo_renglon_registro_documento['registro_principal'] = True
    anterior_renglon_registro_documento.update(registro_principal=False)
    nuevo_renglon_registro_documento['comentarios_renglon'] = f"Motivo de rechazo:\n{datos['motivo_rechazo']}"
    respuesta = {
      'exito_rechazo_documento': True,
      'id_registro_documento': nuevo_renglon_registro_documento['id_registro_documento']
    }
  finally:
    anvil.server.task_state['respuesta'] = respuesta
    sleep(2)
    
@anvil.server.callable
def enviar_documento_a_validacion(datos):
  anterior_renglon_registro_documento = app_tables.calidad_controldocumentos_registrodocumentos.get(id_registro_documento=datos['id_registro_documento'], registro_principal=True)
  info_renglon_documento_actual = dict(anterior_renglon_registro_documento)
  nuevo_renglon_registro_documento = app_tables.calidad_controldocumentos_registrodocumentos.add_row(**info_renglon_documento_actual)
  nuevo_renglon_registro_documento['id_renglon'] = max([r['id_renglon'] for r in app_tables.calidad_controldocumentos_registrodocumentos.search(registro_principal=True)]) + 1
  nuevo_renglon_registro_documento['status'] = 'En validación'
  nuevo_renglon_registro_documento['operacion'] = "Envío a validación"
  nuevo_renglon_registro_documento['id_usuario_registrador'] = datos['id_usuario_registrador']
  nuevo_renglon_registro_documento['marca_temporal'] = datos['marca_temporal']
  anterior_renglon_registro_documento.update(registro_principal=False)
  return [True, nuevo_renglon_registro_documento['id_registro_documento']]

@anvil.server.background_task
def liberar_documento(datos):
  anvil.server.task_state['respuesta'] = {'exito_liberacion_documento': None, 'error':'Comenzó pero no terminó'}
  
  anterior_renglon_registro_documento = app_tables.calidad_controldocumentos_registrodocumentos.get(id_registro_documento=datos['id_registro_documento'], registro_principal=True)
  info_renglon_documento_actual = dict(anterior_renglon_registro_documento)
  nuevo_renglon_registro_documento = app_tables.calidad_controldocumentos_registrodocumentos.add_row(**info_renglon_documento_actual)
  nuevo_renglon_registro_documento['id_renglon'] = max([r['id_renglon'] for r in app_tables.calidad_controldocumentos_registrodocumentos.search(registro_principal=True)]) + 1
  nuevo_renglon_registro_documento['status'] = 'Liberado'
  nuevo_renglon_registro_documento['operacion'] = "Liberación"
  nuevo_renglon_registro_documento['id_usuario_registrador'] = datos['id_usuario_registrador']
  nuevo_renglon_registro_documento['marca_temporal'] = datos['marca_temporal']
  
  dicc_google_script = {
    'id_registro_documento': nuevo_renglon_registro_documento['id_registro_documento'],
    'id_version_documento': nuevo_renglon_registro_documento['id_version_documento'],
    'id_google': nuevo_renglon_registro_documento['id_google'],
    'revision_documento': anterior_renglon_registro_documento['revision'],
    'tipo_app': tipo_google_app(anterior_renglon_registro_documento['tipo_app']),
    'operacion': 'liberacion',
    'fecha_documento': str(datos['fecha_emision']),
    'nivel': nuevo_renglon_registro_documento['nivel']
  }

  if nuevo_renglon_registro_documento['nivel'] == 4:
    dicc_google_script['fecha_formato'] = dicc_google_script['fecha_documento']
    
  respuesta = {}
  anvil.server.task_state['proceso'] = "Comunicando con Google Apps Scripts..."
  
  try:
    respuesta = json.loads(requests.post(url_google_script, data=dicc_google_script).text)['id_doc']
  except Exception as Ex:
    #try / except para borrar la carpeta correspondiente en Google Drive.
    nuevo_renglon_registro_documento.delete()
    respuesta = {
      'exito_liberacion_documento': False,
      'error': f"Tipo de error:\n{type(Ex)}\n\nMensaje de error:\n{Ex}"
    }
  else:
    anterior_renglon_registro_documento.update(registro_principal=False)
    nuevo_renglon_registro_documento['registro_principal'] = True
    nuevo_renglon_registro_documento['fecha_emision'] = datos['fecha_emision']
    respuesta = {
      'exito_liberacion_documento': True,
      'id_registro_documento': nuevo_renglon_registro_documento['id_registro_documento']
    }
  finally:
    anvil.server.task_state['respuesta'] = respuesta
    sleep(2)
    
@anvil.server.callable
def enviar_email_notificacion(datos):
  renglon_documento = app_tables.calidad_controldocumentos_registrodocumentos.get(id_registro_documento=datos['id_registro_documento'], registro_principal=True)
  emails_destinatarios = []
  dicc_nombres = {}
  for sub_equipo in ('creadores', 'revisores', 'validadores'):
    dicc_nombres[sub_equipo] = []
    for id_usuario_erp in renglon_documento[sub_equipo]:
      renglon_usuario_erp = app_tables.sistemas_usuarios_erp_registro.get(id_registro_usuario=id_usuario_erp, registro_principal=True)
      renglon_empleado = app_tables.rh_empleados_infobase.get(id_registro_empleado=renglon_usuario_erp['id_registro_empleado'], registro_principal=True)
      dicc_nombres[sub_equipo].append(str(renglon_empleado['nombre_completo']))
      emails_destinatarios.append(str(renglon_empleado['email_laboral']))
  emails_destinatarios = list(set(emails_destinatarios))
  dicc_status = {
    'creación': ['elaboración', 'creadores'],
    'revisión': ['revisión','revisores'],
    'Rechazo': ['reelaboración', 'creadores'],
    'validación': ['validación final', 'validadores'],
    'Liberación': []
    }
  clave = str(datos['operacion']).split()[-1]
  
  if datos['operacion'] == 'creación':
    asunto = f"Nuevo documento {renglon_documento['codigo']} generado."
    mensaje = f"Un registro de <b>nuevo documento</b> ha sido generado bajo la referencia <b>{renglon_documento['nombre_completo']}</b> y está listo para comenzar a trabajar en él."
  
  elif datos['operacion'] == "revisión":
    asunto = f"Solicitud de {dicc_status[clave][0]} del nuevo documento {renglon_documento['codigo']}."
    mensaje = f"El nuevo documento <b>{renglon_documento['nombre_completo']}</b> ha sido <b>enviado a revisión</b>."

  elif datos['operacion'] == "validación":
    asunto = f"Solicitud de {dicc_status[clave][0]} del nuevo documento {renglon_documento['codigo']}."
    mensaje = f"El nuevo documento <b>{renglon_documento['nombre_completo']}</b> ha sido <b>enviado a validación final</b>."

  elif datos['operacion'] == 'Rechazo':
    asunto = f"Rechazo del nuevo documento {renglon_documento['codigo']}."
    mensaje = f"El nuevo documento <b>{renglon_documento['nombre_completo']}</b> ha sido <b>rechazado durante la {datos['origen_rechazo']}</b>. <p><b>Motivo(s) de rechazo:</b> <p>{datos['motivo_rechazo']}"
  
  elif datos['operacion'] == 'Liberación':
    asunto = f"Liberación del nuevo documento {renglon_documento['codigo']}."
    mensaje = f"El nuevo documento <b>{renglon_documento['nombre_completo']}</b> ha sido <b>liberado</b> y está listo para uso productivo."

  if datos['operacion'] != 'Liberación':
    mensaje += f"<p>Responsable(s) de llevar a cabo la {dicc_status[clave][0]} del documento:"
    for nombre in dicc_nombres[dicc_status[clave][1]]:
      mensaje += f"<p>•{nombre}"
    
  mensaje += f"<p><p><b>Sistema ERP | Ensel Technologies</b>"
  try:
       
    anvil.google.mail.send(
      to = emails_destinatarios,
      subject = asunto,
      html = "<b> == MÓDULO DE CALIDAD / CONTROL DE DOCUMENTOS ==</b><p><p>" + mensaje
    )
  except Exception as Ex:
    return [False, f"Tipo de error:\n{type(Ex)}\n\nMensaje de error:\n{Ex}"]
  else:
    return [True]
  
@anvil.server.callable
def obtener_historial_documento(id_registro_documento):
  return sorted(list(app_tables.calidad_controldocumentos_registrodocumentos.search(id_registro_documento=id_registro_documento)), key=lambda d:d['marca_temporal'], reverse=True)

@anvil.server.callable
def obtener_info_empleado(id_usuario_erp):
  renglon_usuario_erp = app_tables.sistemas_usuarios_erp_registro.get(id_registro_usuario=id_usuario_erp, registro_principal=True)
  renglon_empleado = app_tables.rh_empleados_infobase.get(id_registro_empleado=renglon_usuario_erp['id_registro_empleado'], registro_principal=True)
  return renglon_empleado['nombre_completo'], renglon_empleado['numero_empleado']

@anvil.server.callable
def obtener_nombres_equipo_de_trabajo(equipo_id_usuarios):
  equipo_nombres = {}
  equipo_id_usarios = {}
  for sub_equipo in ('creadores', 'revisores', 'validadores'):
    equipo_nombres[sub_equipo] = []
    for id_usuario_erp in equipo_id_usuarios[sub_equipo]:
      nombre_empleado, numero_empleado = obtener_info_empleado(id_usuario_erp)
      equipo_nombres[sub_equipo].append(f"{nombre_empleado} ({numero_empleado})")
  return equipo_nombres

@anvil.server.callable
def obtener_renglon_documento(id_registro_documento):
  return dict(app_tables.calidad_controldocumentos_registrodocumentos.get(id_registro_documento=id_registro_documento, registro_principal=True))

@anvil.server.callable
def obtener_id_registro(nombre_completo):
  return app_tables.calidad_controldocumentos_registrodocumentos.get(nombre_completo=nombre_completo, registro_principal=True)['id_registro_documento']

@anvil.server.callable
def lanzar_background_task_obtener_documentos_existentes():
  return anvil.server.launch_background_task('obtener_documentos_existentes')

@anvil.server.background_task
def obtener_documentos_existentes():
  anvil.server.task_state['progreso'] = "Cargando..."
  renglones_tipos_documento = [dict(r) for r in app_tables.calidad_controldocumentos_tipodocumentos.search()]
  tipos_documento = {renglon['codigo']: renglon['tipo'] for renglon in renglones_tipos_documento}
  renglones_areas = [dict(r) for r in app_tables.calidad_controldocumentos_areas.search()]
  areas = {renglon['codigo']: renglon['area'] for renglon in renglones_areas}
  renglones_empleados = [dict(r) for r in app_tables.rh_empleados_infobase.search(registro_principal=True)]
  empleados = {str(renglon['id_registro_empleado']): renglon['nombre_completo'] + f" ({renglon['numero_empleado']})" for renglon in renglones_empleados}
  renglones_usuarios = [dict(r) for r in app_tables.sistemas_usuarios_erp_registro.search(registro_principal=True)]
  usuarios = {str(renglon['id_registro_usuario']): empleados[str(renglon['id_registro_empleado'])] for renglon in renglones_usuarios}
  renglones_documentos = [dict(r) for r in app_tables.calidad_controldocumentos_registrodocumentos.search(registro_principal=True, registro_activo=True)]
  documentos_base = {str(renglon['id_registro_documento']): renglon['nombre_completo'] for renglon in renglones_documentos}
  #REGRESAR SIGUIENTE LINEA SINO FUNCIONA!
  documentos_existentes = sorted(renglones_documentos, key=lambda d:d['nombre_completo'])#sorted([dict(r) for r in app_tables.calidad_controldocumentos_registrodocumentos.search(registro_principal=True, registro_activo=True)], key=lambda d:d['nombre_completo'])
  for documento in documentos_existentes:
    documento.update(
      {
        'tipo_documento': tipos_documento[documento['codigo'][0:3]],
        'area': areas[documento['codigo'][4:7]],
        'propietario': usuarios[str(documento['id_usuario_propietario'])],
        'fecha_emision': "" if documento['fecha_emision'] == None else str(documento['fecha_emision'])
      }
    )
    if documento['id_documento_base'] != None:
      documento['documento_base'] = documentos_base[str(documento['id_documento_base'])]
  anvil.server.task_state['progreso'] = "Terminado"
  anvil.server.task_state['items'] = documentos_existentes
  #return documentos_existentes

@anvil.server.callable
def obtener_ids_equipo_de_documento(nombre_documento):
  renglon_documento = app_tables.calidad_controldocumentos_registrodocumentos.get(nombre_completo=nombre_documento, registro_activo=True, registro_principal=True)
  ids_usuarios_equipo_trabajo = list(renglon_documento['creadores'])
  ids_usuarios_equipo_trabajo.extend(renglon_documento['revisores'])
  ids_usuarios_equipo_trabajo.extend(renglon_documento['validadores'])
  ids_usuarios_equipo_trabajo = list(set(ids_usuarios_equipo_trabajo))
  return ids_usuarios_equipo_trabajo

@anvil.server.callable
def obtener_documentos_registrados():
  return app_tables.calidad_controldocumentos_registrodocumentos.search(registro_principal=True, registro_activo=True)

@anvil.server.callable
def obteter_tipos_documentos():
  return 