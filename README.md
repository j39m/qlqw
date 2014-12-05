qlqw is the poor man's kludge for making sure the Quod Libet queue is safe without quitting Quod Libet (forcing it to write said queue) and restart it. 

# 4 December 2014: All new qlqw, now with infinitely more Perl! 

pqlqw is qlqw recast as a Perl script. I spent less than two hours Googling around for the requisite Perl to hack it together. It has the same functionality as the C version, but I daresay it's less clumsy. By the gods I don't know what possessed me to write this originally in C. 

The main difference in pqlqw is that the dry-run flag is now "-n" ("no" write) instead of "-c" ("check" to be sure). The default mode is to write, i.e. no arguments. 

~~You can build qlqw by running "make qlqw." "make clean," sweeps all the created garbage under the carpet. Naturally, you will need to have a decently up-to-date version of QuodLibet installed (and running) for qlqw to work. You will also need libcurl and (of course) gcc.~~

~~To actually _use_ qlqw, simply execute the outputted binary (the makefile names it "qlqw") and your queue file will be written to reflect the current state of your queue. If you would like to inspect what is being written as a dry-run, pass the "-c" flag and nothing will be written --- instead, qlqw will print to stdout.~~

qlqw makes a hilarious number of awful assumptions, including the exact formatting of the output of "quodlibet --print-queue," the location of QuodLibet's queue file, and the maximum length of the user's filenames (including full paths). Use caution. Make use of the "-n" flag for a dry run. 
