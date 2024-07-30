#!/usr/bin/perl
# mailbox options form
#
require './functions-lib.pl';
&ReadParse();

sub ACLrow
{
my ($user, $acl, $n)=@_;
print "\n<tr>\n<td $cb>", unix_user_input("user$n", $user, 2), "</td>\n<th $cb>";
foreach $car (@ACLS)
    {
    print "$car<input type=checkbox name=", $car, "$n value=1";
    print " checked" if $acl =~ /$car/;
    print ">\n";
    }
print "</th>\n<td $cb>";
print "<input type=button onClick=delACL('$user') value='", $text{remove}, "'>" if $user;
print "</td></tr>\n";
return ++$n;
}

iframe_header(); print "<center>";

$confdel=$text{conf_del_mailbox};
$confacl=$text{conf_del_acl};
$mbox=$in{mbox};

print <<JS;
<SCRIPT>
function Confirm()
{ return confirm("$confdel"); }

function delACL(user)
{ 
if (confirm("$confacl "+user+"?")) 
    location.href="mbox_acl.cgi?mbox="+escape('$mbox')+"&delACL="+user;
}
</SCRIPT>
JS

$cyrus = &cyrus_connect();
check_mailbox($mbox) if $mbox;
$quota=0;
get_config();

unless ($mbox)
	{
# create a new mailbox at the root level
	print "<br><br><br>
	<table border=1 cellpadding=2>
	<form method=post action=mbox_create.cgi onSubmit=convquota(this)>
	<tr><th $cb>", $text{create_mbox}, " <input name=mbox size=35 onBlur=checkName(this)>&nbsp;&nbsp;&nbsp;",
	$text{mbox_user}, "<input type=checkbox name=user value=1 checked></th>
	<td $cb rowspan=3><input value='", $text{create}, "' type=submit></td></tr>
	<tr><th $cb>", $text{partition}, ": ";
	defaultpartition();
	print "</td></tr>\n<tr> <th $cb>", $text{set_quota}, " ";
	print ui_bytesbox("quota", trim($imapParams{autocreatequota}*1024), 6);
	print "</th></tr> </form> </table>"; 
	}
else
	{
# display the mailbox infos within a form to change them
	@list=$cyrus->list($mbox); 
#	$entry=$list[0];
#	($mbox, $attributes, $sep) = ($entry->[0],$entry->[1],$entry->[2]);
	($name, $supmbox, $messages, $size, $partition) = mbox_info($mbox,2);
	print "<table border=1 cellpadding=2>
	
	<form method=post action=mbox_manage.cgi onSubmit=convquota(this)>
	<input name=mbox value='$mbox' type=hidden>
	<tr><td colspan=2 align=center $cb><B>",
	    name_decode($mbox), "</B><BR>";
    if (!$supmbox || $supmbox eq 'user')
        {	    
	    ($quota, $used)=getquota($mbox);
        print $text{messages}, ": $messages - ", $text{mbox_size}, ": ", byteFormat($size);
        print "<br>quota: ", byteFormat($quota), " - ", $text{used}, ": $used" if $quota>0;
        }
    else 
        { 
        print $text{messages}, ": $messages - ", $text{folder_size}, ": ", byteFormat($size);
        } 
	print "</td></tr>
	<tr><th $tb>", $text{partition}, " ";
	defaultpartition($partition);
	$rwsp=(!$supmbox || $supmbox eq 'user')? 2 : 1;
	print "</th><th rowspan=$rwsp $tb><input value='", $text{set}, "' name=update type=submit></th></tr>";
    print "<tr> <th $tb>quota ", ui_bytesbox("quota", $quota, 6), "
        <input type=submit value=\"", $text{requota1},  "\" name=requota> </th></tr>" 
        if $rwsp == 2;
	print "</tr>
		<tr><th colspan=2 $tb>", $text{subfolder}, " <input name=folder size=35> 
		<input name=create value='", $text{create}, "' type=submit></th></tr>
		
		<tr><th colspan=2 $cb>", $text{this_mbox}, ":
		<input type=submit name=rebuild value='", $text{rebuild}, "'>
		<input onClick='return Confirm()' name=delete value='", $text{delete}, 
		"' type=submit> </form> 

		<form method=post action=mbox_move.cgi>
        <input name=mbox value='$mbox' type=hidden>\n";
    if (!$supmbox || $supmbox eq "user") 
        {
        $copy=1;    
        print $text{copy_mbox}, " <input name=copymbox>&nbsp;&nbsp;&nbsp;",
	    $text{mbox_user}, "<input type=checkbox name=user value=1 checked>
		<input type=submit name=copy value='", $text{copy}, "'>\n";
        }
    if ($supmbox ne "user")
        {
        print "<br>" if $copy;
        print $text{move_mbox};
#        if ($imapParams{virtdomains}==1)         
        print <<JSTREE;
<SCRIPT>
re='';
if (parent.frames[0].domain) re = new RegExp('\@'+parent.frames[0].domain);
document.write('<SELECT NAME=newparent> <OPTION></OPTION>');
for (var i in parent.frames[0].aMbox)
    { 
    item = parent.frames[0].aMbox[i];
    if (re) item=item.replace(re,'');
    document.write('<OPTION>'+item+'</OPTION>'); 
    }
document.write('</SELECT>\\n / <input size=10 name=newname>');
if (re) document.write( re.source + '<INPUT TYPE=HIDDEN NAME=domain VALUE='+re.source+'>');
</SCRIPT>
JSTREE
        print "<input type=submit name=rename value='", $text{move}, "'>\n";
        }

    print "</form> 

        </th> </tr> </table> <br> 

        <form method=post action=mbox_acl.cgi><input name=mbox value='$mbox' type=hidden>
		<table border=1 cellpadding=2>
		<tr><th $tb>", $text{user}, "</th><th $tb>ACLs</th><th $tb>&nbsp;</th></tr>";

# list ACLs
    %acls=$cyrus->listacl($mbox);
    $n=0;
    while (($user,$acl)=each (%acls))
        {
        next if $user eq $config{admin_user};
        $n=ACLrow($user, $acl, $n);
        }
    ACLrow("","",$n);
    print "<tr><th colspan=3 $tb><input name=setACL type=submit value='", $text{set}, 
        "'></td></tr></table></form>";
	}
print "\n</center>

<SCRIPT>
function convquota(f)
{
pow=f.quota_units.selectedIndex;
pow=f.quota_units.options[pow].value/1024.0;
f.quota.value=f.quota.value*pow;
}

function checkName(c)
{";

if ($imapParams{virtdomains}!=0) { print " return;"; }
else
    {
    print '
var re = /@.+/;
c.value = c.value.replace(re,"");
';
    }
    
print "}
</SCRIPT></BODY></HTML>";