#! /usr/bin/env perl

use strict; 
use warnings; 
use Getopt::Std; 
# we need URI unescaping for Quod Libet's queue-printing style.
use URI::Escape; 

# what do you want? 
my %flags = (); 
# "-h" flag gets brief help, "-n" flag provides dry run to stdout.
getopts ("hn", \%flags);

if (defined $flags{h}) { 
print "Have a look at the readme! pqlqw doesn't require much explanation.\n" and exit; 
} 

# look for a running instance of Quod Libet: 
my $username = $ENV{"LOGNAME"}; 
# pgrep Quod Libet by username, surpressing output 
my $returnzeroplz = system(join(" ", "pgrep -u", $username, 
    "quodlibet > /dev/null"));
# Did we find Quod Libet? 
if ($returnzeroplz != 0) { 
  print "Quod Libet isn't running!\n"; 
  exit 
} 

# Okay, let's grab the queue according to Quod Libet.
my $q_contents = `quodlibet --print-queue | cut -c 8-650`; 
# the cut pipe above trims off "file://" from the output.
# don't forget to unescape encodings on the queue contents. 
$q_contents = uri_unescape($q_contents); 

# lovely. now we need the user's home directory
my $userhome = $ENV{"HOME"}; 
# from which we build the Quod Libet queue path 
my $qp = join ("/", $userhome, ".quodlibet", "queue"); 

# two things can happen here: either the "-n" flag is set, meaning
# that we are not to write, but to print to stdout what the write
# would look like; or the "-n" flag is *not* set, meaning we go
# ahead and write. We can check if it's set: 

if (defined $flags{n}) { 
  print $q_contents; 
} else { 
  # now let's open the queue file for writing: 
  open (q_file, "> $qp") or die "couldn't open $qp\n"; 
  # AND NOW LET US WRITE: 
  print q_file $q_contents;
} 

exit; 
