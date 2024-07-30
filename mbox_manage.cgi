#!/usr/bin/perl
# mailbox managing
#
require './functions-lib.pl';
&ReadParse();

iframe_header();

my $err="", $root="", $reload=0;
my $mbox=$in{mbox};
$mbox="user" if $in{user};
$cyrus = &cyrus_connect();

if ($mbox)
	{
	check_mailbox($mbox);
#	$entry=$list[0]; ($mbox, $attributes, $sep) = ($entry->[0],$entry->[1],$entry->[2]);
	($name, $supmbox, $partition) = mbox_info($mbox,1);
    $cyrus->setacl($mbox, $config{admin_user}=>"all");
	}

# create new mailbox or subfolder
if ($in{create})
	{ 
    ($mbox, $domain) = split /@/, $mbox;
	$mbox = $mbox.$SEP.name_encode($in{folder});
	$mbox .= '@'.$domain if $domain;
	$cyrus->create($mbox,$in{defaultpartition}); 
	$err=$cyrus->error."<BR>\n";
	if ($in{quota} && !$err) 
		{ $cyrus->setquota($mbox, 'STORAGE', $in{quota}); }
	$err=$cyrus->error;
	msglog("create mailbox ".name_decode($mbox)) unless $err;
	$reload=1;
	}
	
# delete mailbox 
if ($in{delete})
	{ 
	$cyrus->delete($mbox); 
	$err=$cyrus->error;
	if (!$err)
		{
		msglog("delete mailbox ".name_decode($mbox));
        ($mbox, $domain) = split /@/, $mbox;
		$mbox=$supmbox;
	    $mbox .= '@'.$domain if $domain;		
		}
	$reload=1;
	}

# rebuild mailbox 
if ($in{rebuild})
	{
    %acls=$cyrus->listacl($mbox); 
    $cyrus->setacl($mbox, $config{admin_user}=>"all") unless $acls{$config{admin_user}} eq "lrswipcda";    
	$cmd=$config{lib_path}."/reconstruct";
	if (-e $cmd)
		{
        system "su -c '$cmd \"$mbox\"' cyrus"; 
        print "<br>";
        msglog($text{rebuild}." ".name_decode($mbox));
        }
   	else 
        {
        print "<BR><BR>$cmd ", $text{not_found}, "<BR>", $text{go_to_config};
        exit;
        }
	}

# recheck quota
if ($in{requota})
	{
	$cmd=$config{lib_path}."/quota";
	if (-e $cmd)
		{
        $cmd=`su -c '$cmd -f \"$mbox\"' cyrus 2>&1 `; 
        print "<PRE>$cmd</PRE><br>";
        msglog($text{requota1}." ".name_decode($mbox));
        }
   	else 
        {
        print "<BR><BR>$cmd ", $text{not_found}, "<BR>", $text{go_to_config};
        exit;
        }
	}
	
# update quota and/or partition
if ($in{update})
	{ 
	($quota, $used)=getquota($mbox);
	if ($in{quota} != $quota*1024)
		{
        $quotacmd=$config{lib_path}."/quota";	
        unless (-e $quotacmd)
            {
			print "<BR><BR>$quotacmd ", $text{not_found}, "<BR>", $text{go_to_config};
			exit;
			}
		if ($in{quota}>0)
		    {
#	modify the quota in the root mailbox! (not in all subfolders!)
            $cyrus->setquota($mbox, 'STORAGE', $in{quota});
            $err=$cyrus->error;
            msglog("set quota $in{quota} on ".name_decode($mbox)) unless $err;
            }
		else
#	remove the quota in mailbox and all subfolders
            {
            my $findName=$mbox; $findName =~ s/^user.//; $findName =~ s/\./^/g;
            my @list=split /\n/,`find $config{imap_path}/quota -type f -name *$findName*`;
            foreach (@list) { unlink $_; }
            msglog("remove quota from ".name_decode($mbox));
            }
        print "<PRE>", `su -c '$quotacmd -f $mbox' cyrus 2>&1`, "</PRE><br>";
		}

	get_partitions() unless %imapPartitions;
	if ($imapPartitions{$in{defaultpartition}} ne $partition)
		{
#	move the mailbox to another partition
		$cyrus->rename($mbox,$mbox,$in{defaultpartition});
		$err=$cyrus->error;
		msglog("move ".name_decode($mbox)." to $in{defaultpartition} partition") unless $err;
		}
	}

iframe_footer($mbox, $err, $reload);
