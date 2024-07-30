#!/usr/bin/perl
# Manage the IMAP partitions

require './functions-lib.pl';
&ReadParse();

&ui_print_header(undef,$text{'partitions'}, undef);

if ($in{apply}) { &stop; &start; } 

if ($in{create})
	{
	my $mkimap=$config{lib_path}."/mkimap";
	unless (-e $mkimap)
		{
        print "<BR><BR>$mkimap ", $text{not_found}, "<BR>", $text{go_to_config};
        exit;
		}
	system "mkdir $in{path}" unless -d $in{path};
	system "chmod 0700 $in{path}";
	$id="id ".$config{admin_user}; $id=`$id`; $id =~ /uid=(\d+).+gid=(\d+)/;
	system "chown $1:$2 $in{path}";
	@lines=();
	open CONF, $config{imapd_conf_path};
	while (<CONF>) { push @lines, $_ if trim($_); }
	close CONF;
	open CONF, ">".$config{imapd_conf_path};
	foreach (@lines)
		{
		print CONF;
		print CONF "partition-".$in{name}.": ".$in{path}."\n"
			if /partition-default/;
		}
	close CONF;
	system "su -c '$mkimap \"".$in{path}."\"' cyrus";
    &webmin_log("make IMAP partition $path");
	$restart=1;
	}

if ($in{delete})
	{
	system "rm -fR $in{delete}";
	open CONF, $config{imapd_conf_path};
	while (<CONF>) { push @lines, $_; }
	close CONF;
	open CONF, ">".$config{imapd_conf_path};
	foreach (@lines)
		{
		print CONF unless index($_,$in{delete})>0;
		}
	close CONF;
	$restart=1;
	}

# get values
get_config();
get_partitions();

# get the EXAMINE output
$infocmd=$config{lib_path}."/mbexamine";
if (-e $infocmd)
	{
    @res=split /\n/, `su -c '$infocmd' cyrus`;
	}
else 
	{
	print "<BR><BR>$infocmd ", $text{not_found}, "<BR>", $text{go_to_config};
	exit;
	}

print "<FORM ACTION=partitions.cgi> <TABLE CELLPADDING=2 BORDER=1>
	<TR><TH $tb>", $text{'name'}, "</TH><TH $tb>", $text{'path'}, 
	"</TH><TH $tb>", $text{'folders'}, "</TH><TH $tb>-</TH></TR>\n";
while (($name,$path) = each %imapPartitions)
	{	
	print "<TR><TD $cb>$name";
	print " [*]" if $name eq $defaultPartition; 
	print "</TD><TD $cb>$path</TD>";
	$folders=0; reset @res;
	foreach (@res) { $folders++ if /$path/; }
	print "<TD $cb>$folders</TD><TD $cb>";
	if ($name eq 'default' || $name eq $defaultPartition || $folders)
		{ print "-"; }
	else
		{
		print "<A HREF=\"partitions.cgi?delete=$path\" TITLE='", 
		$text{'delete'}, "'><IMG HSPACE=2 SRC=images/cestino.gif BORDER=0></A>";
		}
	print "</TD></TR>\n";
	}
print "<TR><TD $cb><INPUT NAME=name SIZE=15></TD><TD $cb>\n<INPUT NAME=path SIZE=30>",
	&file_chooser_button('path',1), 
	"\n</TD><TH COLSPAN=2 $cb><INPUT TYPE=SUBMIT NAME=create VALUE='", $text{create},
	"'></TH></TR>\n</TABLE>[*] = default";
print '&nbsp;&nbsp;<INPUT TYPE=SUBMIT NAME=apply VALUE="', $text{'apply'}, '">' if $restart;
print "</FORM>";

&ui_print_footer("index.cgi", $text{'index_title'});


