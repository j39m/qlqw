qlqw is a stupid, poorly written, and overall quite sad program that professes to enhance your QuodLibet experience. It actually lets you write a live queue to disk! By using qlqw, you no longer need restart QuodLibet just to be paranoid about making sure your queue is saved. qlqw prints out the _current_ contents of your queue in the same format as the queue file (stored at ~/.quodlibet/queue, written only on a clean exit from QL). You can pipe the output of qlqw to the queue file. 

Be warned: I am quite serious when I say qlqw is poorly written. It isn't documented, uses unnecessarily bloated methods, and makes really, really unsafe assumptions. It is by no means meant for general consumption, as it most certainly can and will mess things up. 

You can build qlqw by running "make qlqw." "make clean," naturally, sweeps all the created garbage under the carpet. Naturally, you will need to have a decently up-to-date version of QuodLibet installed (and running) for qlqw to work. 

qlqw makes a hilarious number of awful assumptions, including the exact formatting of the output of "quodlibet --print-queue," the location of QuodLibet's queue file, and the maximum length of the user's filenames (including full paths). It's bad, bad, bad. I will work slowly to make it better. But I can't imagine anyone needing to actually use this particular tidbit of code; it's mostly for my own gratification. 
