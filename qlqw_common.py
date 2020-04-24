# This module contains common boilerplate for the qlqw family.
# It should be installed alongside other plugin templates packaged
# with Quod Libet.
#
# This code is licensed under the 3-Clause BSD License.

import os
import threading

from gi.repository import Gtk, GLib

import quodlibet
from quodlibet import _
from quodlibet import qltk
from quodlibet.plugins.events import EventPlugin
from quodlibet.plugins import PluginConfig
from quodlibet.qltk import Icons
from quodlibet.qltk.msg import Message
from quodlibet.util.dprint import print_d
from quodlibet.errorreport import errorhook

class QlqwError(RuntimeError):
    pass

class IoOnSongChangePluginBackend:
    """Provides threaded I/O."""

    def __init__(self):
        self.called_event = threading.Event()

    def fire(self):
        """
        Arms this backend to perform I/O. Called from the main
        plugin context.
        """
        self.called_event.set()

    def _run_loop(self):
        self.called_event.wait()
        self.called_event.clear()

    def run_loop(self):
        """
        Main entry point of this class. Waits for the main plugin
        context to request a queue write. Operates from the I/O context.
        """
        while True:
            try:
                self._run_loop()
            except Exception:
                errorhook()

class IoOnSongChangePlugin(EventPlugin):
    """
    This class does nothing but deliver queue write requests to the
    backend (residing in a separate I/O thread). It does not fail
    meaningfully, deferring error handling to said backend.
    """

    PLUGIN_ID = "XXX PLUGIN_ID NOT SET"
    PLUGIN_NAME = _("XXX PLUGIN_NAME NOT SET")
    PLUGIN_DESC = _("XXX PLUGIN_DESC NOT SET")
    PLUGIN_ICON = Icons.DIALOG_ERROR

    QLQW_BACKEND_TYPE = IoOnSongChangePluginBackend

    def __init__(self):
        self.__enabled = False
        self.logging_enabled = False
        self.backend = self.QLQW_BACKEND_TYPE()

        backend_thread = threading.Thread(None, self.backend.run_loop)
        backend_thread.setDaemon(True)
        backend_thread.start()

    def log(self, message):
        if self.logging_enabled:
            print_d("{}: {}".format(self.PLUGIN_ID, message))

    def plugin_on_song_started(self, song):
        if not self.__enabled:
            return

        self.log("reacting to song change.")
        # TODO(j39m): rate-limit the present method.
        self.backend.fire()

    def enabled(self):
        self.__enabled = True
        self.log("enabled.")

    def disabled(self):
        self.__enabled = False
        self.log("disabled.")
