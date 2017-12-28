# qlqw

... is the poor man's kludge for making sure the Quod Libet queue is safe
without quitting Quod Libet (forcing it to write said queue) and restart it.
qlqw uses inotify to figure out when it should write the queue.
