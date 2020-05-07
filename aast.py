# This code is licensed under the 3-Clause BSD License.

import os
import signal
import subprocess

from gi.repository import Gtk, GLib

from quodlibet import app
from quodlibet.plugins.events import EventPlugin
from quodlibet.qltk import Icons
from quodlibet.commands import _print_playing

class EllipsisNeededError(RuntimeError):
    pass

def write_bytes(characters, allowed_bytes, tfp, allow_partial=True):
    """Returns number of bytes written to |tfp|."""
    as_bytes = bytes(characters, "utf-8")

    if len(as_bytes) <= allowed_bytes:
        tfp.write(characters)
        return len(as_bytes)

    if not allow_partial:
        raise EllipsisNeededError()

    writable_length = allowed_bytes
    while writable_length:
        try:
            characters_to_write = as_bytes[:writable_length].decode("utf-8")
            break
        except UnicodeDecodeError:
            writable_length -= 1
    tfp.write(characters_to_write)
    raise EllipsisNeededError()

class AlwaysAvailSongTitle(EventPlugin):

    PLUGIN_ID = "always-avail-song-title"
    PLUGIN_NAME = "Always Avail Song Title"
    PLUGIN_DESC = "Avails song title to i3status on song change."
    PLUGIN_ICON = Icons.DIALOG_ERROR

    TARGET_FILE = os.path.join(
        os.getenv("XDG_RUNTIME_DIR"),
        "quodlibet-current-title.txt"
    )
    USERNAME = os.getenv("USERNAME")
    ELLIPSIS = " ..."
    ABSOLUTE_MAX_TITLE_WIDTH = 120
    ELLIPSISED_MAX_TITLE_WIDTH = ABSOLUTE_MAX_TITLE_WIDTH - len(ELLIPSIS)

    def __init__(self):
        self.__enabled = False

    def greedily_write_bytes(self, split_title, tfp):
        """
        Greedily writes as many bytes and escaped ampersands ("&amp;")
        as possible. Never leaves |tfp| s.t. it ends in a partial
        ampersand or in invalid UTF-8.

        |split_title| is a list of title fragments, having been split
        on ampersand characters.
        """
        bytes_until_ellipsis = self.ELLIPSISED_MAX_TITLE_WIDTH
        bytes_until_maximum = self.ABSOLUTE_MAX_TITLE_WIDTH

        for (index, char_sequence) in enumerate(split_title):
            is_last_loop = index == len(split_title) - 1
            if is_last_loop:
                # Here's a real mess: if we can fit the last run
                # squarely into the _total_ allowed characters, there's
                # no need for ellipsis.
                if (len(bytes(char_sequence, "utf-8"))
                        <= bytes_until_maximum):
                    write_bytes(char_sequence, bytes_until_maximum, tfp)
                    return
                write_bytes(char_sequence, bytes_until_ellipsis, tfp)
                assert False, "BUG: expected write_bytes() to raise \
                        EllipsisNeededError()"

            bytes_written = write_bytes(char_sequence, bytes_until_ellipsis,
                                        tfp)
            bytes_until_ellipsis -= bytes_written
            bytes_until_maximum -= bytes_written

            bytes_written = write_bytes("&amp;", bytes_until_ellipsis,
                                        tfp, allow_partial=False)
            bytes_until_ellipsis -= bytes_written
            bytes_until_maximum -= bytes_written

    def write_title(self):
        raw_title = _print_playing(app, fstring=u"<title>")

        with open(self.TARGET_FILE, "w") as tfp:
            try:
                self.greedily_write_bytes(raw_title.split("&"), tfp)
            except EllipsisNeededError:
                tfp.write(self.ELLIPSIS)

    def notify_i3status(self):
        pgrep_output = subprocess.check_output((
            "pgrep", "-u", self.USERNAME, "-x", "i3status")).strip()
        try:
            i3status_pid = int(pgrep_output)
        except ValueError:
            return

        if i3status_pid > 1:
            os.kill(i3status_pid, int(signal.SIGUSR1))

    def plugin_on_song_started(self, _song):
        if not self.__enabled:
            return

        self.write_title()
        self.notify_i3status()

    def enabled(self):
        self.__enabled = True

    def disabled(self):
        self.__enabled = False
