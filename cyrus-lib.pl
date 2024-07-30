#!/usr/bin/perl
do '../web-lib.pl';
&init_config();
require '../ui-lib.pl';

use Cyrus::IMAP::Admin;
$HOSTNAME=get_system_hostname();
$HOMESITE="www.tecchio.net";
$HOMEPAGE="webmin/cyrus";

$SEP = "cat ".$config{imapd_conf_path}." | grep unixhierarchysep";
$SEP = `$SEP` =~ /(\d+)/; 
$SEP = ($SEP == 1)? '/' : '.'; 

sub cyrus_connect 
{
# connects to Cyrus server, and returns a handler    
my $cyrus;
if (`ps -A | grep cyrus` || `ls /var/run/cyrus*`)
    { $cyrus = Cyrus::IMAP::Admin->new('localhost',$config{imap_port});  }
unless ($cyrus)
    {
    print $text{unable_connect} . " $HOSTNAME<br>" . $text{go_to_config} . "<br><br>";
    return 0;
    }
$cyrus->authenticate(-user=>$config{admin_user}, -password=>$config{admin_password}) 
    or $err=$text{unable_auth}."  ".$config{admin_user}."<br>".$text{go_to_config}."<br>";
if ($err) { print $err; return 0; }
else { return $cyrus; }
}

sub cyrus_error() 
{
if ($err != 0) {print '<SCRIPT> alert("', $cyrus->error, '"); history.back(); </SCRIPT>';}
}

sub start
# start the server
{
print $text{start_cyrus}, "...";
&error_setup($text{'start_err'});
$temp = &tempname();
$rv = &system_logged("($config{'initscript'} start) >$temp 2>&1");
$out = `cat $temp`; unlink($temp);
if ($rv) {
	&error("<pre>$out</pre>");
	}
sleep(3);
&webmin_log("start Cyrus"); print "OK! ";
}


sub stop
# stop the server
{
print $text{stop_cyrus}, "...";
$out = &backquote_logged("$config{'initscript'} stop 2>&1");
&error_setup($text{'stop_err'});
if ($?) {
	&error("<pre>$?\n$out</pre>");
	}
&webmin_log("stop Cyrus"); print "OK! ";
}

sub get_config
{
# get the configuration parameters
%imapParams=();
open(MYFILE,$config{imapd_conf_path}) 
	or die "<BR><BR>".$config{imapd_conf_path}." ".$text{not_found}."<BR>".$text{go_to_config};
while(<MYFILE>)
	{
	next if /^#/;
	chop;
	s/\"//g;
	if (/(.+):\s*(.+)$/)
		{ $imapParams{$1}=$2; }
	}
close MYFILE;
}

sub trim 
{
# a trim function 
my $string = shift;
for ($string) 
	{
	s/^\s+//;
	s/\s+$//;
	}
return $string;
}

sub perldeps
{
my $err="";
foreach (@_)
    {
    eval "use $_"; 
    $err.="<LI>$_</LI>\n" if $@ ne '';
    }
if ($err)
    {
    print $text{no_perl_libs}, ":<UL>$err</UL>\n";
    exit;
    }
}
1;