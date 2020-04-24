# This code is licensed under the 3-Clause BSD License.

import os
import signal
import subprocess

from gi.repository import Gtk, GLib

import quodlibet
from quodlibet import _
from quodlibet import app
from quodlibet.plugins.events import EventPlugin
from quodlibet.qltk import Icons
from quodlibet.commands import _print_playing

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
    I3STATUS_BLOCK_MAX_CHAR_WIDTH = 120
    MAX_TITLE_WIDTH = I3STATUS_BLOCK_MAX_CHAR_WIDTH - 4

    def __init__(self):
        self.__enabled = False

    def write_title(self, song):
        title = _print_playing(app, fstring=u"<title>")

        with open(self.TARGET_FILE, "w") as tfp:

            if len(title) > self.I3STATUS_BLOCK_MAX_CHAR_WIDTH:
                tfp.write(title[:self.MAX_TITLE_WIDTH])
                tfp.write(" ...")
                return

            tfp.write(title)

    def notify_i3status(self):
        pgrep_output = subprocess.check_output((
            "pgrep", "-u", self.USERNAME, "-x", "i3status")).strip()
        try:
            i3status_pid = int(pgrep_output)
        except ValueError:
            return

        if i3status_pid > 1:
            os.kill(i3status_pid, int(signal.SIGUSR1))

    def plugin_on_song_started(self, song):
        if not self.__enabled:
            return

        self.write_title(song)
        self.notify_i3status()

    def enabled(self):
        self.__enabled = True

    def disabled(self):
        self.__enabled = False
