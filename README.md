qlqw is a stupid, poorly written, and overall quite sad program that professes to enhance your QuodLibet experience. It actually lets you write a live queue to disk! By using qlqw, you no longer need restart QuodLibet just to be paranoid about making sure your queue is saved. Be warned: I am quite serious when I say qlqw is poorly written. It isn't documented, uses unnecessarily bloated methods, and makes really, really unsafe assumptions. It is by no means meant for general consumption, as it most certainly can and will mess things up. 

~~You can build qlqw by running "make qlqw." "make clean," sweeps all the created garbage under the carpet. Naturally, you will need to have a decently up-to-date version of QuodLibet installed (and running) for qlqw to work. You will also need libcurl and (of course) gcc.~~

~~To actually _use_ qlqw, simply execute the outputted binary (the makefile names it "qlqw") and your queue file will be written to reflect the current state of your queue. If you would like to inspect what is being written as a dry-run, pass the "-c" flag and nothing will be written --- instead, qlqw will print to stdout.~~

All new qlqw, now with infinitely more Perl! 

qlqw makes a hilarious number of awful assumptions, including the exact formatting of the output of "quodlibet --print-queue," the location of QuodLibet's queue file, and the maximum length of the user's filenames (including full paths). I will say it again: it is horrible. Don't use it. 
