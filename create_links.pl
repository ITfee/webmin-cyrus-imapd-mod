#!/usr/bin/perl
# post-install script (typical for Debian, but useful in any situation
# where the third party modules are in another directory)

@files=('web-lib.pl','ui-lib.pl');
foreach $file (@files)
	{
	unless (-e "../$file")
		{
		print "find /usr -type f -name $file... ";
		$fpos=`find /usr -type f -name $file | grep webmin`;
		chop $fpos;
		if ($fpos) 
			{ 
			print " create link in ../$file<BR>";
			system "ln -s $fpos ../$file";
			die "Unable to create link to $file" unless -l "../$file";
			}
		}
	}
