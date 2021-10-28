# EDMC Tritium Mining Calculator Plugin

Simple, no configuration needed. Displays a cumulative count of tritium rocks vs total prospected, average percent tritium found vs tritium rocks *and* total prospected rocks, and total tons mined/tons per hour rate. Calculates over the whole session, from the first rock prospected or ton refined to the last of either. Reset clears the counters and starts over.

If you *want* a little configuration, there's an option to write out files (`TC-*.txt`) for all the various data collected/calculated, which's handy for streaming overlays and such. It does *not* preserve data between sessions, etc.

## Installation

  * On EDMC's Plugins settings tab press the “Open” button. This reveals the `plugins` folder where EDMC looks for plugins.
  * Download the [latest release](https://github.com/poisonbl/TritiumCalculator/releases/latest) of this plugin.
  * Open the `.zip` archive that you downloaded and move the `TritiumCalculator` folder contained inside into the `plugins` folder.

  _You will need to re-start EDMC for it to notice the new plugin._

## Other
A special thanks for a few pieces I borrowed from LILTTALK/StreamSource, and the testing and feature ideas from CMDR Deluvian's crew.
