import tkinter as tk
import myNotebook as nb
import logging
import l10n
import functools
import os
import time
from io import open	# For Python 2&3 a version of open that supports both encoding and universal newlines
from os.path import join

from typing import Optional, Tuple, Dict, Any
from config import appname, config

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f'{appname}.{plugin_name}')

_ = functools.partial(l10n.Translations.translate, context=__file__)

laststate: Optional[Dict[str, Any]] = None

data = {
  "Prospected":0,
  "Hit":0,
  "ReturnHits":0,
  "ReturnProspected":0,
  "ReturnTotal":0,
  "Mined":0,
  "TonsPerHour":0,
  "First":0,
  "Last":0,
  "TimeSpent":0,
  "outdir":config.get_str('outdir'),
  "WriteFiles":tk.BooleanVar(value=config.get_bool("TC-WriteFiles")),
}

def plugin_start3(plugin_dir: str) -> str:
  global plugin_name
  logger.debug('Plugin loaded')
  return plugin_name

def plugin_stop() -> None:
  pass

def prefs_changed(cmdr: str, is_beta: bool) -> None:
  global data
  if data["outdir"] != config.get_str('outdir'):
     data["outdir"] = config.get_str('outdir')
  config.set('TC-WriteFiles', data['WriteFiles'].get())
  write_all()

def plugin_prefs(parent: nb.Notebook, cmdr: str, is_beta: bool) -> Optional[tk.Frame]:
  global data
  data["WriteFiles"] = tk.BooleanVar(value=config.get_bool("TC-WriteFiles"))  # Retrieve saved value from config
  frame = nb.Frame(parent)
  nb.Label(frame, text='Settings:').grid(row=0,column=0,sticky=tk.W)
  # nb.Label(frame, text='Write Files').grid(row=1,column=0,sticky=tk.W)
  nb.Checkbutton(frame,text='Write Files',variable=data["WriteFiles"],onvalue=True,offvalue=False).grid(row=1,column=0,sticky=tk.W)
  return frame

def plugin_app(parent) -> Tuple[tk.Label,tk.Label]:
  global data

  frame = tk.Frame(parent)
  data["l1"] = tk.Label(frame, text=_('Rocks found: '))
  data["v1"] = tk.Label(frame, text='? (?)')
  data["l1"].grid(row=0,column=0,sticky=tk.W)
  data["v1"].grid(row=0,column=1)
  data["l2"] = tk.Label(frame, text=_('Return rate found (vs total): '))
  data["v2"] = tk.Label(frame, text='? (?)')
  data["l2"].grid(row=1,column=0,sticky=tk.W)
  data["v2"].grid(row=1,column=1)
  data["l3"] = tk.Label(frame, text=_('Mined: '))
  data["v3"] = tk.Label(frame, text='? (?)')
  data["l3"].grid(row=2,column=0,sticky=tk.W)
  data["v3"].grid(row=2,column=1)
  data["resetb"] = tk.Button(frame, text=_('Reset'),command=reset)
  data["resetb"].grid(row=3,column=0,columnspan=2)
  write_all()
  update_status()
  return (frame)

def journal_entry(
  cmdr: str, is_beta: bool, system: str, station: str, entry: Dict[str, Any], state: Dict[str, Any]
) -> None:
  global data

  if entry['event'] == "MiningRefined" and entry['Type'] == "$tritium_name;":
    if data["First"] == 0:
      data["First"] = time.time()
    data["Last"] = time.time()
    data["TimeSpent"] = data["Last"]-data["First"]
    data["Mined"] += 1
    data["TonsPerHour"] = 3600*data["Mined"]/data["TimeSpent"] if data["TimeSpent"]>0 else data["Mined"]
    write_file("TC-Mined.txt",l10n.Locale.string_from_number(data["Mined"],0))
    write_file("TC-TonsPerHour.txt",l10n.Locale.string_from_number(data["TonsPerHour"],2))
    write_file("TC-TimeSpent.txt",l10n.Locale.string_from_number(data["TimeSpent"],2))
    update_status()

  elif entry['event'] == "ProspectedAsteroid":
    if data["First"] == 0:
      data["First"] = time.time()
    data["Last"] = time.time()
    data["TimeSpent"] = data["Last"]-data["First"]
    for mat in entry['Materials']:
      if mat['Name'] == "Tritium":
        data['ReturnTotal'] += mat['Proportion']
        data['Hit'] += 1
        data["ReturnHits"] = data["ReturnTotal"]/data["Hit"] if data["Hit"]>0 else 0
        write_file("TC-ReturnTotal.txt",l10n.Locale.string_from_number(data['ReturnTotal'],2))
        write_file("TC-Hit.txt",l10n.Locale.string_from_number(data['Hit'],4))
        write_file("TC-ReturnHits.txt",l10n.Locale.string_from_number(data["ReturnHits"],2))
    data["Prospected"] += 1
    data["ReturnProspected"] = data["ReturnTotal"]/data["Prospected"] if data["Prospected"]>0 else 0
    write_file("TC-Prospected.txt",l10n.Locale.string_from_number(data["Prospected"],0))
    write_file("TC-ReturnProspected.txt",l10n.Locale.string_from_number(data["ReturnProspected"],2))
    write_file("TC-TimeSpent.txt",l10n.Locale.string_from_number(data["TimeSpent"],2))
    update_status()

def update_status() -> None:
  global data
  data["v1"]['text'] = '{} Hit ({} Total)'.format(
    l10n.Locale.string_from_number(data["Hit"],0),
    l10n.Locale.string_from_number(data["Prospected"],0))
  data["v2"]['text'] = '{}% ({}%)'.format(
    l10n.Locale.string_from_number(data["ReturnHits"],2),
    l10n.Locale.string_from_number(data["ReturnProspected"],2))
  data["v3"]['text'] = '{} t ({} t/hr)'.format(
    l10n.Locale.string_from_number(data["Mined"],0),
    l10n.Locale.string_from_number(data["TonsPerHour"],2))

def reset() -> None:
  global data
  logger.debug("Resetting.")
  logger.debug(data)
  data["Prospected"] = 0
  data["Hit"] = 0
  data["ReturnHits"] = 0
  data["ReturnProspected"] = 0
  data["ReturnTotal"] = 0
  data["Mined"] = 0
  data["TonsPerHour"] = 0
  data["First"] = 0
  data["Last"] = 0
  data["TimeSpent"] = 0
  write_all()
  update_status()

# write one file
def write_file(name, text=None):
  global data
  if not data['WriteFiles'] or not data['WriteFiles'].get():
    return
  # File needs to be closed for the streaming software to notice its been updated.
  with open(join(data["outdir"], name), 'w', encoding='utf-8') as h:
    h.write(u'%s\n' % (text or u''))
    h.close()

def write_all():
  write_file("TC-Prospected.txt",l10n.Locale.string_from_number(data["Prospected"],0))
  write_file("TC-Hit.txt",l10n.Locale.string_from_number(data['Hit'],0))
  write_file("TC-ReturnHits.txt",l10n.Locale.string_from_number(data["ReturnHits"],2))
  write_file("TC-ReturnProspected.txt",l10n.Locale.string_from_number(data["ReturnProspected"],2))
  write_file("TC-ReturnTotal.txt",l10n.Locale.string_from_number(data['ReturnTotal'],2))
  write_file("TC-Mined.txt",l10n.Locale.string_from_number(data["Mined"],0))
  write_file("TC-TonsPerHour.txt",l10n.Locale.string_from_number(data["TonsPerHour"],2))
  write_file("TC-TimeSpent.txt",l10n.Locale.string_from_number(data["TimeSpent"],2))
