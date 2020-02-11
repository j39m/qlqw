# qlqw

`qlqw` is a utility that writes the contents of your Quod Libet queue
to disk on every song change.

## qlqw

The `qlqw` script is a standalone executable that uses inotify (together
with some predictable but undocumented behavior exhibited by Quod Libet)
to detect song changes.

## qlqw\_ng.py

`qlqw_ng.py` is cast as an event plugin for Quod Libet. It uses the
standard plugin hooks that Quod Libet exposes to determine when the song
changes.
