#!/usr/bin/perl
# display the mailboxes tree with virtual domains support

sub getInfos
{
my ($name, $parent, $domain)=mbox_info(@_,0);
$name="<I>$name</I>" unless $parent;
if ($parent eq 'user' || !$parent) { $parent = "foldersTree"; }
elsif ($domain) { $parent .= '@'.$domain; }
return ($name, $parent);
}

print "<DIV ALIGN=RIGHT><A TARGET=mainFrame HREF=mbox_info.cgi>$text{create_mbox}</A></DIV>\n";

if (!$q->param('domain'))
    {
    $nDom=1;        
    %localDomains=($imapParams{defaultdomain}=>1); 
    foreach $entry (@list) 
        {
        ($name, $parent, $domain)=mbox_info($entry->[0],0);
        if ($domain) { $localDomains{$domain}=1; $nDom++; }
        }
    if ($nDom>1)
        {        
        print "<B>$text{localdomains}:</B>\n<UL>\n";
        foreach (sort keys %localDomains)
            { print "<LI><A HREF=tree.cgi?domain=$_>$_</A></LI>\n"; }
        }            
    }

if ($q->param('domain')) { $myDomain = $q->param('domain'); }
if ($nDom == 1) { $myDomain = $imapParams{defaultdomain}; }

if ($myDomain)
    {
    print <<START;
<A HREF=frames.html TARGET=_parent>$text{localdomains}</A><BR>    
<SCRIPT SRC=treeMenu/ua.js></SCRIPT>
<SCRIPT SRC=treeMenu/ftiens4.js></SCRIPT>

<SCRIPT>
USETEXTLINKS = 0;
STARTALLOPEN = 0;
ICONPATH = 'treeMenu/';
WRAPTEXT = 1;
aMbox=new Array(); n=0;
foldersTree = gFld("<b>$myDomain</b>");
START

    use Tree::Simple;
    $root = Tree::Simple->new("/", Tree::Simple->ROOT);
    $mboxes{"foldersTree"}=$root;

    foreach $entry (@list) 
        {
        if ($myDomain eq $imapParams{defaultdomain})
            { next if index($entry->[0],'@')>0 && $entry->[0] !~ /\@$myDomain$/; }
        else
            { next unless $entry->[0] =~ /\@$myDomain$/; }
        ($name, $parent)=getInfos($entry->[0]);
        ($name, $domain)=split /\@/, $name;
        $value = "$name#$parent#$entry->[0]";
        $mboxes{$entry->[0]} = Tree::Simple->new($value,$mboxes{$parent});  
        print "aMbox[n++]=\"$entry->[0]\";\n"; 
        }

# traverse the tree and output the result
    $root->traverse(
        sub {
        my $node = shift;
        my ($name, $parent, $entry) = split /#/, $node->getNodeValue();
        $parent =~ s/\W/_/g; $parent =~ s/^user//;
        if ($node->isLeaf())
            {
            print "insDoc($parent, gLnk('R','$name','mbox_info.cgi?mbox='+escape('$entry')));\n";
            }
        else
            {
            $value = $entry; $value =~ s/\W/_/g; $value =~ s/^user//;
            print "$value=insFld($parent, gFld('$name','mbox_info.cgi?mbox='+escape('$entry')));\n";
            }
        }
    );
  
    print "domain='$myDomain';\n" unless $myDomain eq $imapParams{defaultdomain};
    
    print <<END;
</SCRIPT>    
<DIV STYLE="position:absolute; top:0; left:0;">
<TABLE BORDER=0><TR><TD>
    <A HREF="http://www.treemenu.net/" TARGET=_blank></A>
</TD></TR></TABLE></DIV>
<!-- Build the browser objects and display default view of the tree. -->
</BODY>	 
<SCRIPT> 
url="tree.cgi";
initializeDocument(); 

function setWidth()
{
if (document.width)
	{
	wLeft=document.width;
	wRight=parent.frames[1].document.width;
	}
if (document.body.clientWidth)
	{
	wLeft=document.body.clientWidth;
	wRight=parent.frames[1].document.body.clientWidth;
	}	
if (wLeft && wRight)
	{	
	wLeft=parseInt(wLeft/(wLeft+wRight)*100); 
	top.frames[0].setCookie("wLeft",wLeft);
	}
}

onresize=setWidth;

</SCRIPT>
END
    }

1;