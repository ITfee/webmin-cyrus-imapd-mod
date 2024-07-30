#!/usr/bin/perl
# copy or move a mailbox to another
#
require './functions-lib.pl';
&ReadParse();

iframe_header();

my $err="", $root="", $reload=0;
$cyrus = &cyrus_connect();
my $mbox=$in{mbox};

check_mailbox($mbox);
@list=$cyrus->list($mbox); $entry=$list[0]; $oldmbox=$entry->[0];
#($oldmbox, $attributes, $sep) = ($entry->[0],$entry->[1],$entry->[2]);
($name, $supmbox, $partition) = mbox_info($mbox,1);

# rename a mailbox
if ($in{rename} && $in{newname})
    {
    $copymbox=$in{newname};
    if ($in{domain}) { $copymbox.=$in{domain}; }
    if ($in{newparent}) { $copymbox=$in{newparent}.$SEP.$copymbox; }
    $cyrus->rename($mbox,name_encode($copymbox));    
    $err=$cyrus->error;
    unless ($err)
        {
        $reload=1;
        msglog("move ".name_decode($mbox)." to ".$copymbox);
        }
    }

if ($in{copy} && $in{copymbox})
    {
# get the partition name
    get_config() unless %imapParams;
    while (($k,$v)=each %imapParams) 
        { 
        if ($v eq $partition) { $k =~ /^partition-(.+)/; $partition=$1; }
        }

    $copymbox=$in{copymbox};
    $copymbox="user$SEP$copymbox" if $in{user};

    use Mail::IMAPClient;
    my $imap = Mail::IMAPClient->new(Server => 'localhost',
				User => $config{admin_user},
				Password => $config{admin_password},
				Uid => 1,
				Peek => 1,
				Buffer => 4096,
				Fast_io => 1,
				) or die("Cannot connect to Cyrus IMAP as a client - $!");

    push @list, $cyrus->list($mbox.$SEP."*"); 
    foreach $entry (@list)
        {
        my $mbox = $entry->[0];            
#        my ($mbox, $attributes, $sep) = ($entry->[0],$entry->[1],$entry->[2]);        
	    my ($quota, $root, $used)=getquota($mbox);

# create the new mailbox
        $newmbox=$mbox; $newmbox =~ s/$oldmbox/$copymbox/i;
        $cyrus->create(name_encode($newmbox),$partition); 
        $err=$cyrus->error;
        last if $err;
        msglog("create mailbox $newmbox");
        $cyrus->deleteacl(name_encode($newmbox), name_encode($in{copymbox}));
        last if $err;
        $reload=1;   
# set quota	
        if ($root eq $mbox && $quota) 
	        { 
            $cyrus->setquota(name_encode($newmbox), 'STORAGE', $quota); 
            $err=$cyrus->error;
            last if $err;
            msglog("set quota $quota on $newmbox");
            }
# copy ACLs
        %acls=$cyrus->listacl($mbox);
        while (($user,$acl)=each (%acls))
            {
        $cyrus->setacl(name_encode($newmbox), $user => $acl);
        $err=$cyrus->error;
        last if $err;
        msglog("set ACL $user => $acl on $newmbox");
        }
# copy messages
        $imap->select($mbox);
        next if $imap->message_count == 0;
        my $uidlist = $imap->copy(name_encode($newmbox), $imap->messages);
        if (defined($uidlist)) { msglog("copy msg $uidlist to $newmbox"); }
        else { $err="Error copying messages to $newmbox"; }
        last if $err;
        }
    $imap->close;        
    }

iframe_footer($copymbox,$err,$reload);

