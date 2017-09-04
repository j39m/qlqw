#!/usr/bin/env perl 

use strict; 
use warnings; 

$SIG{"INT"} = "catch_sigint"; 

my @nothing = ();
my $klaus = join("\n", @nothing);
if ($klaus) {
    print "$klaus\n";
} else {
    print "NOTHING!\n";
}

for (@nothing) {
    print "HELLO!\n";
}

sub catch_sigint { 
  my $klaus = "";
  if ($klaus) {
    print "HELLO\n";
  }
  print "gotcha!\n"; 
  exit(); 
} 
