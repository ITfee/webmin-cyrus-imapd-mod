#!/usr/bin/perl
# ACL managing
#
require './functions-lib.pl';
&ReadParse();
iframe_header();

my $err="", $root="", $reload=0;
my $mbox=$in{mbox};

$cyrus = &cyrus_connect();

if ($mbox)
	{
	check_mailbox($mbox);
    @list=$cyrus->list($mbox.$SEP."*"); 
    unshift @list, $cyrus->list("$mbox"); 
	}

# set the ACLs of the mailbox and all subfolders
if ($in{setACL})
    {
# first, delete all ACLs (except the admin!)
    %acls=$cyrus->listacl($mbox);
    while (($user,$acl)=each (%acls))
        {
        next if $user eq $config{admin_user};        
        foreach (@list)
            {
	        $cyrus->deleteacl($_->[0], $user);
	        $err=$cyrus->error;
	        msglog("delete ACL $user on ".name_decode($_->[0])) unless $err;
	        }
        }
    $n=0; $err="";
    while ($in{"user$n"} && !$err)
        {
        my $myACL="";
        foreach $acl (@ACLS) { $myACL.=$acl if $in{$acl.$n}==1; }
        foreach (@list)
            {
            $cyrus->setacl($_->[0], $in{"user$n"}=>$myACL);
            $err=$cyrus->error;
            msglog("set ACL ".$in{"user$n"}." on ".name_decode($_->[0])) unless $err;	
            }
        $n++;
        }
    }

# delete an ACL of the mailbox and all subfolders
if ($in{delACL})
	{ 
    foreach (@list)
        {
	    $cyrus->deleteacl($_->[0], $in{delACL});
	    $err=$cyrus->error;
	    msglog("delete ACL $in{delACL} on ".name_decode($_->[0])) unless $err;
	    }
	}

iframe_footer($mbox,$err,$reload);