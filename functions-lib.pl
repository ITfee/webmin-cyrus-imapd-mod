#!/usr/bin/perl
do 'cyrus-lib.pl';

use Encode qw/encode decode/;
use HTML::Entities;
@ACLS=('l','r','s','w','i','p','c','d','a');
@aHost=split /\./,$HOSTNAME; $ext=pop @aHost; $domain=pop @aHost;
$DEFDOMAIN="$domain.$ext";

sub check_mailbox{
# checks if a mailbox exists
	my $path=shift;
	my @list = $cyrus->list($path);
	&cyrus_error();

	if ($#list!=0) {
	    print '<SCRIPT> alert("', $text{unknown_mbox}, ': ', name_decode($path), '"); history.back(); </SCRIPT>';
	}
}

sub mbox_info
{
# get mailbox information
# arguments: mailbox name, return mode
# mode=0 or null: returns $name, $supmbox, $domain;
# mode=1: 	returns $name, $supmbox, $partition;
# mode=2: 	returns $name, $supmbox, $messages, $size, $partition
my $mbox=shift; my $mode=shift; my @paths=(), $n=0, $i=0;
while ($i>-1)
    {
    $i=index($mbox,$SEP,$n);
    if ($i>-1) 
        {
        push @paths, substr($mbox,$n,$i-$n);
        $n=$i+1;
        }
    }
my ($name, $domain)=split /\@/,$mbox; 
$name = name_decode(substr($mbox,$n));
my $supmbox = join($SEP,@paths);

return ($name, $supmbox, $domain) if $mode==0;

get_partitions() unless %imapPartitions;
my $partition="";
my $infocmd=$config{lib_path}."/mbpath";
if (-e $infocmd)
	{
    my $res=`su -c '$infocmd \"$mbox\"' cyrus`;
	while (($k, $v)=each %imapPartitions)
		{
		if (index($res,$v)>=0) { $partition=$v; last; }
		}
	return ($name, $supmbox, $partition) if $mode==1;
	}
else 
	{
	print "<BR><BR>$infocmd ", $text{not_found}, "<BR>", $text{go_to_config};
	exit;
	}

my $messages=0, $size=0;
$infocmd=$config{lib_path}."/mbexamine";
if (-e $infocmd)
	{
    @res=split /\n/, `su -c '$infocmd \"$mbox\"' cyrus`;
	foreach (@res)
		{
		if (/Number of Messages:\s+(\d+)\s+Mailbox Size:\s+(\d+)\s+bytes/)
			{
			$messages+=$1; 
			$size+=$2;
			}
		}
	}
else 
	{
	print "<BR><BR>$infocmd ", $text{not_found}, "<BR>", $text{go_to_config};
	exit;
	}
return ($name, $supmbox, $messages, $size, $partition);
}

sub get_services
{
# get the list of services managed by Cyrus    
@cyrusServs=();
open(MYFILE,$config{cyrus_conf_path}) 
	or die "<BR><BR>".$config{cyrus_conf_path}." ".$text{not_found}."<BR>".$text{go_to_config};
while(<MYFILE> !~ /^SERVICES \{/) {}
while(<MYFILE>)
	{ 
	last if /^\}/;
	if (/^(#?)\s*(\w+)\s+cmd=/)
			{ push @cyrusServs, "$1:$2"; }
	}
close MYFILE;
}

sub get_partitions
{
# get the imap partitions    
get_config() unless %imapParams;
%imapPartitions=(); $defaultPartition="default";
while (($k,$v)=each %imapParams) 
	{ 
	if ($k =~ /^partition-(.+)/) { $imapPartitions{$1}=$v; }
	$defaultPartition=$v if $k eq "defaultpartition";
	}
}

# function to select the default partition
sub defaultpartition
{ 
my $value=shift;
get_partitions();
$value=$defaultPartition unless $value;
$value="default" unless $value; 
print "<SELECT NAME=defaultpartition>\n";
while (($k,$v)=each %imapPartitions) 
	{ 
	print "<OPTION VALUE=$k";
	print " SELECTED" if $value eq $k || $value eq $v;
	print ">$k: $v</OPTION>\n";
	}
print "</SELECT>\n";
}

sub getquota
{
# get used and quota amount, and perc.used, if it's a root folder
my $mbox=shift;
my %quotas, $elems;
($mbox, %quotas)=$cyrus->quotaroot($mbox);
$elems=$quotas{'STORAGE'};
return ($elems->[1]*1024, trim(sprintf("%9.2f %", $elems->[0]/$elems->[1]*100))) if $elems->[1];
return (0, 0) unless $elems->[1];
}

# functions to encode-decode international 
#    characters in mailbox names
sub name_encode
{
my $name=shift;    
$name=encode("UTF-7", $name);
$name =~ s/\+/&/g;
return $name;
}

sub name_decode
{
my $name=shift;    
$name =~ s/&/\+/g; 
$name=decode("UTF-7", $name);
return encode_entities($name);
}

sub byteFormat
{
my $size=shift;
Case: {
if ($size < 1024) { $size.=" byte"; last Case; }
if ($size < 1024*1024) { $size=sprintf("%9.2f Kb",$size/1024); last Case; }
if ($size < 1024*1024*1024) { $size=sprintf("%9.2f Mb",$size/1024/1024); last Case; }
$size=sprintf("%9.2f Gb", $size/1024/1024/1024);
} 
my ($val,$unit)=split / /,trim($size); $val =~ s/\.*0+$// unless $unit eq 'byte';
return "$val $unit";
}

sub msglog
{
my $msg=shift;
&webmin_log($msg);
print "$msg: OK<BR>\n";
}

sub iframe_header
{
print "Content-type: text/html

<HTML><BODY>
<SCRIPT>
if (top.document.styleSheets.length>0) 
    {
    document.write('<LINK REL=stylesheet HREF='+top.document.styleSheets[0].href+'>');\n";
if ($_[0]) 
    {
    print "\t}\ndocument.write(\"<body $_[0]>\");\n"; 
    }    
else
    {
    print "\tdocument.write('<body>');
    }
else if (top.document.body.bgColor) 
    document.write('<body bgcolor=' + top.document.body.bgColor +
	    ' topmargin=1 leftmargin=1 marginwidth=1 marginheight=1>');\n";
    }	    
print "</SCRIPT>\n<P>\n";
}    

sub iframe_footer
{
my ($name, $err, $reload)=@_;    
print "<BR><FONT COLOR=red><B>$err</B></FONT><BR>\n" if $err;
print "<SCRIPT> parent.frames[0].location.reload(); </SCRIPT>" if $reload;
print "<FORM><INPUT TYPE=BUTTON VALUE='";
if (!$name || $name eq 'user')
    { print &text('main_return', '/'), "' onClick=\"location.href='mbox_info.cgi'\">"; }
else 
    { print &text('main_return', name_decode($name)), "' onClick=\"location.href='mbox_info.cgi?mbox='+escape('$name')\">"; }
print "\n </FORM>\n</BODY></HTML>";    
}

1;