# This code is licensed under the 3-Clause BSD License.

"""
qlqw dumps your queue into ${XDG_RUNTIME_DIR} on every song change.
"""

import os
import threading
import urllib.parse

from gi.repository import Gtk, GLib

from quodlibet import _
from quodlibet import app
from quodlibet.plugins.events import EventPlugin
from quodlibet.qltk import Icons
from quodlibet.util.dprint import print_d
from quodlibet.errorreport import errorhook
from quodlibet import commands

LOGGING_IS_ENABLED = False


class QlqwError(RuntimeError):
    """Do-nothing exception specific to qlqw."""


class QlqwBackend:
    """Provides threaded I/O for queue writing."""

    FILE_PREFIX = "file://"
    TARGET_PATH = os.path.join(
        os.getenv("XDG_RUNTIME_DIR"),
        "qlqw.txt"
    )

    def __init__(self):
        self.called_event = threading.Event()
        self.last_queue_hash = None

    def parse_queue(self, dumped_queue_string):
        parsed = list()

        for line in urllib.parse.unquote(dumped_queue_string).splitlines():
            if not line.startswith(self.FILE_PREFIX):
                raise QlqwError("unexpected queue entry: ``{}''".format(line))

            path = line[len(self.FILE_PREFIX):]
            if not os.path.exists(path):
                raise QlqwError("nonexistent queue entry: ``{}''".format(path))

            parsed.append(path)

        return parsed

    def get_queue(self):
        dumped_string = commands.registry.run(app, "dump-queue")
        queue_hash = hash(dumped_string)
        if not dumped_string or queue_hash == self.last_queue_hash:
            return None

        self.last_queue_hash = queue_hash
        return self.parse_queue(dumped_string)

    def commit_queue(self, queue_list):
        with open(self.TARGET_PATH, "w") as qfp:
            for line in queue_list:
                qfp.write(line)
                qfp.write("\n")

    def get_and_commit_queue(self):
        queue_list = self.get_queue()
        if queue_list is not None:
            self.commit_queue(queue_list)

    def fire(self):
        """
        Arms this backend to write the queue. Called from the main
        plugin context.
        """
        self.called_event.set()

    def _run_loop(self):
        self.called_event.wait()
        self.called_event.clear()
        self.get_and_commit_queue()

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


class Qlqw(EventPlugin):
    """
    This class does nothing but deliver queue write requests to the
    backend (residing in a separate I/O thread). It does not fail
    meaningfully, deferring error handling to said backend.
    """

    PLUGIN_ID = "qlqw"
    PLUGIN_NAME = _("Write Queue Aggressively")
    PLUGIN_DESC = _("Commits queue contents to disk on every song "
                    "change.")
    PLUGIN_ICON = Icons.DIALOG_ERROR

    def __init__(self):
        self.__enabled = False
        self.backend = QlqwBackend()

        backend_thread = threading.Thread(None, self.backend.run_loop)
        backend_thread.setDaemon(True)
        backend_thread.start()

    def plugin_on_song_started(self, song):
        if not self.__enabled:
            return

        # TODO(j39m): rate-limit the present method.
        self.backend.fire()

    def enabled(self):
        self.__enabled = True

    def disabled(self):
        self.__enabled = False
