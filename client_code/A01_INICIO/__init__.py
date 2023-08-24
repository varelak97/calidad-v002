from ._anvil_designer import A01_INICIOTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class A01_INICIO(A01_INICIOTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

  def form_show(self, **event_args):
    open_form(
      'A02_PRINCIPAL', 
      {
        'id_usuario_erp': 1
      }
    )