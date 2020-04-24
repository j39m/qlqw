# This code is licensed under the 3-Clause BSD License.

import os
import signal
import subprocess

from gi.repository import Gtk, GLib

import quodlibet
from quodlibet import _
from quodlibet import app
from quodlibet.plugins.events import EventPlugin
from quodlibet.plugins import PluginConfig
from quodlibet.qltk import Icons
from quodlibet.errorreport import errorhook
from quodlibet.commands import _print_playing

def write_title(song, target_file):
    title = _print_playing(app, fstring=u"<title>")
    with open(target_file, "w") as tfp:
        tfp.write(title)

def notify_i3status(username):
    pgrep_output = subprocess.check_output((
        "pgrep", "-u", username, "-x", "i3status")).strip()
    try:
        i3status_pid = int(pgrep_output)
    except ValueError:
        return
    if i3status_pid > 1:
        os.kill(i3status_pid, int(signal.SIGUSR1))

class AlwaysAvailSongTitle(EventPlugin):

    PLUGIN_ID = "always-avail-song-title"
    PLUGIN_NAME = _("Always Avail Song Title")
    PLUGIN_DESC = _("Avails song title to i3status on song change.")
    PLUGIN_ICON = Icons.DIALOG_ERROR

    TARGET_FILE = os.path.join(
        os.getenv("XDG_RUNTIME_DIR"),
        "quodlibet-current-title.txt"
    )
    USERNAME = os.getenv("USERNAME")

    def __init__(self):
        self.__enabled = False

    def plugin_on_song_started(self, song):
        if not self.__enabled:
            return

        write_title(song, self.TARGET_FILE)
        notify_i3status(self.USERNAME)

    def enabled(self):
        self.__enabled = True

    def disabled(self):
        self.__enabled = False
