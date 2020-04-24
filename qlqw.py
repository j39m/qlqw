# qlqw writes your queue on every song change.
#
# This code is licensed under the 3-Clause BSD License.

import os
import urllib.parse

import quodlibet
from quodlibet import _
from quodlibet import app, qltk
from quodlibet import commands
from quodlibet.qltk import Icons

from quodlibet.plugins.qlqw_common import IoOnSongChangePlugin
from quodlibet.plugins.qlqw_common import IoOnSongChangePluginBackend
from quodlibet.plugins.qlqw_common import QlqwError

class QlqwBackend(IoOnSongChangePluginBackend):

    FILE_PREFIX = "file://"
    TARGET_PATH = os.path.join(quodlibet.get_user_dir(), "qlqw.txt")

    def __init__(self):
        super().__init__()
        self.last_queue_hash = None

    def parse_queue(self, dumped_queue_string):
        parsed = list()

        for line in urllib.parse.unquote(dumped_queue_string).splitlines():
            if not line.startswith(self.FILE_PREFIX):
                raise QlqwError("unexpected queue entry: ``{}''".format(line))

            path = line[len(self.FILE_PREFIX):]
            if not os.path.exists(path):
                raise QlqwError("nonexistent queue entry: ``{}''".format(path))

            parsed.append(path);

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

    def _run_loop(self):
        # Block until there's work to do.
        super()._run_loop()
        self.get_and_commit_queue()


class Qlqw(IoOnSongChangePlugin):

    PLUGIN_ID = "qlqw"
    PLUGIN_NAME = _("Quod Libet Queue Writer")
    PLUGIN_DESC = _("Writes queue on every song change")
    PLUGIN_ICON = Icons.DIALOG_ERROR

    QLQW_BACKEND_TYPE = QlqwBackend
