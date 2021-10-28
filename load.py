import tkinter as tk
import myNotebook as nb
import logging
import l10n
import functools
import os
import time

from typing import Optional, Tuple, Dict, Any
from config import appname


plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f'{appname}.{plugin_name}')

_ = functools.partial(l10n.Translations.translate, context=__file__)

laststate: Optional[Dict[str, Any]] = None

data = {
  "Prospected":0,
  "Hit":0,
  "ReturnHits":0,
  "ReturnTotal":0,
  "Mined":0,
  "First":0,
  "Last":0,
}

def plugin_start3(plugin_dir: str) -> str:
  global plugin_name
  logger.debug('Plugin loaded')
  return plugin_name

def plugin_stop() -> None:
  pass

def plugin_app(parent) -> Tuple[tk.Label,tk.Label]:
  global data

  frame = tk.Frame(parent)
  data["l1"] = tk.Label(frame, text=_('Rocks found (scanned): '))
  data["v1"] = tk.Label(frame, text='? (?)')
  data["l1"].grid(row=0,column=0,sticky=tk.W)
  data["v1"].grid(row=0,column=1)
  data["l2"] = tk.Label(frame, text=_('Return rate (hits/total): '))
  data["v2"] = tk.Label(frame, text='? (?)')
  data["l2"].grid(row=1,column=0,sticky=tk.W)
  data["v2"].grid(row=1,column=1)
  data["l3"] = tk.Label(frame, text=_('Mined tons (/hr): '))
  data["v3"] = tk.Label(frame, text='? (?)')
  data["l3"].grid(row=2,column=0,sticky=tk.W)
  data["v3"].grid(row=2,column=1)
  data["resetb"] = tk.Button(frame, text=_('Reset'),command=reset)
  data["resetb"].grid(row=3,column=0,columnspan=2)
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
    data["Mined"] += 1
    update_status()

  elif entry['event'] == "ProspectedAsteroid":
    if data["First"] == 0:
      data["First"] = time.time()
    data["Last"] = time.time()
    for mat in entry['Materials']:
      if mat['Name'] == "Tritium":
        data['ReturnTotal'] += mat['Proportion']
        data['Hit'] += 1
    data["Prospected"] += 1
    update_status()


def update_status() -> None:
  global data
  if data["First"] == 0 or data["Last"] == 0 or data["Prospected"] == 0 or data["Hit"]:
    data["v1"]['text'] = "? (?)"
    data["v2"]['text'] = "? (?)"
    data["v3"]['text'] = "? (?)"
  else:
    t = data["Last"]-data["First"]
    if t < 1:
      t = 1
    data["v1"]['text'] = '{} / {}'.format(
      l10n.Locale.string_from_number(data["Hit"],0),
      l10n.Locale.string_from_number(data["Prospected"],0))
    data["v2"]['text'] = '{} / {}'.format(
      l10n.Locale.string_from_number(data["ReturnTotal"]/data["Hit"],2),
      l10n.Locale.string_from_number(data["ReturnTotal"]/data["Prospected"],2))
    data["v3"]['text'] = '{} / {}'.format(
      l10n.Locale.string_from_number(data["Mined"],0),
      l10n.Locale.string_from_number(3600*data["Mined"]/t,2))

def reset() -> None:
  global data
  logger.debug("Resetting.")
  logger.debug(data)
  data["Prospected"] = 0
  data["Hit"] = 0
  data["ReturnTotal"] = 0
  data["Mined"] = 0
  data["First"] = 0
  data["Last"] = 0
  update_status()

