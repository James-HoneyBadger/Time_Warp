print "Enter a string: ";
$input = <STDIN>;
chomp($input);

%word_count = ();
foreach $word (split /\s+/, $input) {
    $word =~ s/[^a-zA-Z0-9]//g; # Remove punctuation
    $word = lc($word); # Convert to lowercase
    $word_count{$word}++;
}

print "\nWord Frequency:\n";
foreach $word (sort keys %word_count) {
    print "$word: $word_count{$word}\n";
}

print "Perl demo completed successfully!\n";