#!/usr/bin/perl
use strict;
use warnings;

print "Enter a string: ";
my $input = <STDIN>;
chomp($input);

my %word_count;
foreach my $word (split /\s+/, $input) {
    $word =~ s/[^a-zA-Z0-9]//g; # Remove punctuation
    $word = lc($word); # Convert to lowercase
    $word_count{$word}++;
}

print "\nWord Frequency:\n";
foreach my $word (sort keys %word_count) {
    print "$word: $word_count{$word}\n";
}