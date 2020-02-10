# qlqw_ng: writes your queue on every song change.
#
# This code is licensed under the 3-Clause BSD License.

import os
import threading
import urllib.parse

from gi.repository import Gtk, GLib

import quodlibet
from quodlibet import _
from quodlibet import app, qltk
from quodlibet.plugins.events import EventPlugin
from quodlibet.plugins import PluginConfig
from quodlibet.qltk import Icons
from quodlibet.qltk.msg import Message
from quodlibet.util.dprint import print_d
from quodlibet.errorreport import errorhook
from quodlibet import commands

class QlqwError(RuntimeError):
    pass

class QlqwBackend:
    """Provides threaded I/O for queue writing."""

    FILE_PREFIX = "file://"

    def __init__(self):
        self.called_event = threading.Event()
        self.last_error = None
        self.target_path = os.path.join(quodlibet.get_user_dir(), "qlqw.txt")

        # Protects self.last_error.
        self.lock = threading.Lock()

    def set_last_error(self, error):
        with self.lock:
            self.last_error = error

    def clear_last_error(self):
        with self.lock:
            last_error = self.last_error
            self.last_error = None
            return last_error

    def get_queue(self):
        dumped_string = commands.registry.run(app, "dump-queue")

        result = list()
        for line in urllib.parse.unquote(dumped_string).splitlines():
            if not line.startswith(self.FILE_PREFIX):
                raise QlqwError("unexpected queue entry: ``{}''".format(line))
            path = line[len(self.FILE_PREFIX):]
            if not os.path.exists(path):
                raise QlqwError("nonexistent queue entry: ``{}''".format(path))
            result.append(path);

        return result

    def commit_queue(self, queue_list):
        with open(self.target_path, "w") as qfp:
            for line in queue_list:
                qfp.write(line)
                qfp.write("\n")

    def get_and_commit_queue(self):
        queue_list = self.get_queue()
        self.commit_queue(queue_list)

    def fire(self):
        """
        Arms this backend to write the queue. Called from the main
        plugin context.
        """
        # We should signal the caller (main plugin context) that
        # an error previously occurred. They can react appropriately
        # and possibly call us anew if the error is recoverable.
        # This isn't actually thread-safe.
        last_error = self.clear_last_error()
        if last_error is not None:
            raise last_error
        self.called_event.set()

    def run_loop(self):
        """
        Main entry point of this class. Waits for the main plugin
        context to request a queue write. Operates from the I/O context.
        """
        while True:
            self.called_event.wait()
            self.called_event.clear()
            try:
                self.get_and_commit_queue()
            except Exception as e:
                self.set_last_error(e)
                raise e

class Qlqw(EventPlugin):
    PLUGIN_ID = "qlqw_ng"
    PLUGIN_NAME = _("Write Queue Aggressively")
    PLUGIN_DESC = _("Commits queue contents to disk on every song "
                    "change.")
    PLUGIN_ICON = Icons.DIALOG_ERROR

    def __init__(self):
        self.__enabled = False
        self.backend = QlqwBackend()
        self.times_nagged = 0

        def backend_run():
            try:
                self.backend.run_loop()
            except Exception:
                errorhook()

        backend_thread = threading.Thread(None, backend_run)
        backend_thread.setDaemon(True)
        backend_thread.start()

    def log(self, message):
        print_d("{}: {}".format(self.PLUGIN_ID, message))

    def emergency_stop_nag_dialog(self, msg, dialog_type):
        dialog = Message(dialog_type, app.window, self.PLUGIN_NAME, msg)
        dialog.connect("response", lambda dia, resp: dia.destroy())
        dialog.show()

    def emergency_stop(self, triggering_exception):
        self.log("emergency stop: {}".format(triggering_exception))
        self.disabled()
        message = str(triggering_exception)
        if self.times_nagged:
            message = (
                    "{}\n\nHint: disable this plugin, fix your prior "
                    "problem, and re-enable."
            ).format(str(triggering_exception))
        GLib.idle_add(self.emergency_stop_nag_dialog,
                _(message),
                Gtk.MessageType.ERROR)
        self.times_nagged += 1

    def write_queue(self):
        if not self.__enabled:
            raise QlqwError("qlqw_ng is disabled")
        # TODO(j39m): rate-limit the present method.
        self.backend.fire()

    def plugin_on_song_started(self, song):
        self.log("song changed - writing queue.")
        try:
            self.write_queue()
        except Exception as e:
            self.emergency_stop(e)

    def enabled(self):
        self.__enabled = True
        self.times_nagged = 0
        self.log("enabled.")

    def disabled(self):
        self.__enabled = False
        self.log("disabled.")
