#!/usr/bin/perl
# display the mailboxes tree without virtual domains

sub getInfos
{
my ($name, $parent, $domain)=mbox_info(@_,0);
$name="<I>$name</I>" unless $parent;
if ($parent eq 'user' || !$parent) { $parent = "foldersTree"; }
return ($name, $parent);
}

print <<START;
<DIV ALIGN=RIGHT><A TARGET=mainFrame HREF=mbox_info.cgi>$text{create_mbox}</A></DIV>
<SCRIPT SRC=treeMenu/ua.js></SCRIPT>
<SCRIPT SRC=treeMenu/ftiens4.js></SCRIPT>

<SCRIPT>
USETEXTLINKS = 0;
STARTALLOPEN = 0;
ICONPATH = 'treeMenu/';
WRAPTEXT = 1;
aMbox=new Array(); n=0;
foldersTree = gFld("/");
START

use Tree::Simple;
$root = Tree::Simple->new("/", Tree::Simple->ROOT);
$mboxes{"foldersTree"}=$root;

# prepare the mbox tree 
foreach $entry (@list) 
    {
    ($name, $parent)=getInfos($entry->[0]);
    $mboxes{$entry->[0]} = Tree::Simple->new($entry->[0],$mboxes{$parent});  
    print "aMbox[n++]=\"$entry->[0]\";\n"; 
    }

# traverse the tree and output the result
$root->traverse(
    sub {
    my $node = shift;
    my $value = $node->getNodeValue();
    my ($name, $parent)=getInfos($value);
    $parent =~ s/\W/_/g; $parent =~ s/^user//;
    if ($node->isLeaf())
        {
        print "insDoc($parent, gLnk('R','$name','mbox_info.cgi?mbox='+escape('$value')));\n";
        }
    else
        {
        $value =~ s/\W/_/g; $value =~ s/^user//;
        print "$value=insFld($parent, gFld('$name','mbox_info.cgi?mbox='+escape('",
            $node->getNodeValue(), "')));\n";
        }
    }
);

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

1;