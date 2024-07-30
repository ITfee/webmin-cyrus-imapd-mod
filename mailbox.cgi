#!/usr/bin/perl
#
require './functions-lib.pl';
&ReadParse();

if ($in{rebuild})
	{
	&ui_print_header(undef,$text{rebuild}." ".$text{mbox_tree}, undef);
# reset permissions
    my $cyrus = &cyrus_connect();
    @list = $cyrus->list("*"); # Fetch all mailboxes below the current path
    foreach $entry (@list) 
        {
        %acls=$cyrus->listacl($entry->[0]); 
        $cyrus->setacl($entry->[0], $config{admin_user}=>"all") unless $acls{$config{admin_user}} eq "lrswipcda";
        }
# reconstruct    
	$cmd=$config{lib_path}."/reconstruct";
	if (-e $cmd)
		{
        open CMD, "su -c '$cmd' cyrus 2>&1 | ";
        while (<CMD>) { print name_decode($_); } 
        close CMD;
        &webmin_log("rebuild all mailboxes");
        }
    else 
        {
        print "<BR><BR>$cmd ", $text{not_found}, "<BR>", $text{go_to_config};
        exit;
        }
	print "<HR><FORM><INPUT TYPE=BUTTON VALUE=Ok onClick=\"location.href='mailbox.cgi'\"></FORM>
	    </BODY></HTML>";
	exit;
	}

if ($in{requota})
	{
	&ui_print_header(undef,$text{requota2}, undef);
# recalculate quotas
	$cmd=$config{lib_path}."/quota";
	if (-e $cmd)
		{
		print "<PRE>\n";    
        open CMD, "su -c '$cmd -f' cyrus 2>&1 | ";
        while (<CMD>) { print name_decode($_); } 
        close CMD; print "</PRE>";
        &webmin_log("recheck all quotas");
        }
    else 
        {
        print "<BR><BR>$cmd ", $text{not_found}, "<BR>", $text{go_to_config};
        exit;
        }
	print "<HR><FORM><INPUT TYPE=BUTTON VALUE=Ok onClick=\"location.href='mailbox.cgi'\"></FORM>
	    </BODY></HTML>";
	exit;
	}
	
&ui_print_header(undef,$text{'mbox_tree'}, undef, "help", 1, 1, 0, undef, undef, undef,
"<A HREF=mailbox.cgi?rebuild=1>".$text{rebuild}."</A> - <A HREF=mailbox.cgi?requota=1>".$text{requota2}."</A>"
	);

print "
<SCRIPT>
h=screen.availHeight; 
if (h<=600) h=h-300; 
else h=h-330;
document.write('<IFRAME ID=iframe SRC=frames.html HEIGHT='+h+' WIDTH=98%></IFRAME>');
</SCRIPT>
";

&ui_print_footer("index.cgi", $text{'index_title'});

