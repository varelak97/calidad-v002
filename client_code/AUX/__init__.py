from ._anvil_designer import AUXTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class AUX(AUXTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

  def button_1_click(self, **event_args):
    anvil.server.call('aux2')
    Notification("",title="¡TERMINADO!", style="success").show()

