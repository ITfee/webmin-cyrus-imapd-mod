#!/usr/bin/perl
# create a new mailbox at the top level
#
require './functions-lib.pl';
&ReadParse();

iframe_header();

my $err="", $root="", $mbox="";
$cyrus = &cyrus_connect();

#@list=$cyrus->list("user"); $entry=$list[0]; $sep=$entry->[2];

# create the mailbox 
$mbox = name_encode($in{mbox});
$mbox="user".$SEP.$mbox if $in{user};

$cyrus->create($mbox,$in{defaultpartition}); 
$err=$cyrus->error;

unless ($err)
    {
# set admins ACLs        
    $cyrus->setacl($mbox, $config{admin_user}=>"all");
    $err=$cyrus->error;
# set quota    
    if ($in{quota} && !$err) 
		{ $cyrus->setquota($mbox, 'STORAGE', $in{quota}); }
    $err=$cyrus->error;
    msglog("create mailbox ".name_decode($mbox)) unless $err;
    if ($config{'sync_mbox'} && !getpwnam($in{mbox}))
        {
# if the user doesn't exist, remove his ACLs
        $cyrus->deleteacl($mbox, name_encode($in{mbox}));
        $err=$cyrus->error;
        }
    }        

iframe_footer($mbox,$err,1);