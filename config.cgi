#!/usr/bin/perl
# Manage the configuration of imapd.conf

require './functions-lib.pl';
&ReadParse();

@aParams=("activeservices", "defaultpartition", "sasl_pwcheck_method", "allowanonymouslogin", 
	"autocreatequota", "quotawarn", "hashimapspool", "unixhierarchysep", "altnamespace",
    "virtdomains");

%defaults=("activeservices"=>"", "defaultpartition"=>"default", "sasl_pwcheck_method"=>"", 
    "autocreatequota"=>0, "quotawarn"=>0,
	"unixhierarchysep"=>"0", "altnamespace"=>"0", "allowanonymouslogin"=>"0", 
	"hashimapspool"=>"0", "virtdomains"=>"0");

%locals=("sharedprefix"=>"shared","userprefix"=>"user","defaultdomain"=>$DEFDOMAIN);

%types=("activeservices"=>"F", "defaultpartition"=>"F", "sasl_pwcheck_method"=>"F", 
        "autocreatequota"=>"F", "quotawarn"=>"T",
    	"hashimapspool"=>"Y", "allowanonymouslogin"=>"Y", "unixhierarchysep"=>"L",
	    "altnamespace"=>"F", "virtdomains"=>"F");

%alts=( "unixhierarchysep"=>"/ (slash);1;. (dot);0" );

%sizes=("quotawarn"=>3, "autocreatequota"=>7);
%jsChecks=("quotawarn"=>"onBlur=Between(this,0,100)", "autocreatequota"=>"onBlur=IsInt(this)");
%units=("quotawarn"=>"%");

%hDisable=();

# creates a radio button with %alts options
sub my_radio
{
my ($name,$value)=@_;
my @opts=split /;/, $alts{$name};
for (my $i=0; $i<=$#opts; $i+=2)
    {
    print "<INPUT TYPE=RADIO NAME=$name VALUE='$opts[$i+1]'";
    print " CHECKED" if $value eq $opts[$i+1];
    print "> ", $opts[$i], "&nbsp;&nbsp;";
    }
}

sub activeservices
{
get_services();
foreach (@cyrusServs)
    {    
    my ($comm,$serv)=split /:/;
    print "<INPUT NAME=services TYPE=CHECKBOX VALUE=$serv", 
        ($comm ne "#")? " CHECKED" : "", 
        ">$serv ";
    }
}

# function to select the saslauth methoddefault partition
sub sasl_pwcheck_method
{ 
my $value=shift;
my @opts=("auxprop", "saslauthd", "pwcheck");
print "<SELECT NAME=sasl_pwcheck_method>\n";
foreach $opt (@opts) 
	{ 
	print "<OPTION VALUE=$opt";
	print " SELECTED" if $value eq $opt;
	print ">$opt</OPTION>\n";
	}
print "</SELECT>\n";
}

#option box with a text field
sub my_opt_text
{
my ($value, $optName, $textName, $len)=@_;
$len=15 unless $len;
my $text;
if ($imapParams{$textName}) {$text=$imapParams{$textName};}
else {$text=$locals{$textName};}
print "<input type=radio name=$optName value=0";
print " checked" if $value==0;
print " onClick='form.$textName.disabled=true;'> ", $text{'no'}, 
      " <input type=radio name=$optName value=1";
print " checked" if $value==1;
print " onClick='form.$textName.disabled=false;'> ", $text{'yes'}, ": ",
    $text{$textName}, ": <input name=$textName size=$len value='$text'>";    
$hDisable{$optName}=$textName;    
}

# choose an alternate namespace and a shared prefix
sub altnamespace
{ my_opt_text(shift,'altnamespace','sharedprefix'); }

sub autocreatequota
{
my $value=shift;
print ui_bytesbox("autocreatequota", $value*1024, 6);
}

# allow virtual domains
sub virtdomains
{ my_opt_text(shift,'virtdomains','defaultdomain',35); }

sub checkSubParams
{
# check if a param is set; set or unset dependent params    
my ($baseParam, @altParam) = @_;    
if ($imapParams{$baseParam}==1)
	{
	foreach $alt (@altParam)
	    {
        $imapParams{$alt}=$locals{$alt} if !$imapParams{$alt};
        }
	}
else
    {
	foreach $alt (@altParam)  { delete $imapParams{$alt}; }  
    }
}

&ui_print_header(undef,$text{'config'}, undef, "help", 1, 1, 0);
my $restart=0;

if ($in{apply}) { &stop; &start; } 

get_config();

if ($in{update})
	{
# update values	    
	delete $in{update};
# change cyrus.conf
    my @serv=split /\0/, $in{services}; 
    my @lines=(), $p, $ok;
    delete $in{services}; 
	if (@serv)
	    {
# read previous values
    	open CONF, $config{cyrus_conf_path};
    	while (<CONF>) { push @lines, $_; }
    	close CONF;
    	open CONF, ">".$config{cyrus_conf_path};
# write new values
        $ok=0;
    	foreach (@lines)
    	    { 
    	    if ($ok == 2)
    	        {
                if (/^#?\s*(\w+)\s+(cmd=.+)/)
                    {
                    $ok=0;
                    foreach $p (@serv) { $ok=1 if $p eq $1; }
                    print CONF ($ok)? "" : "#", "  $1\t\t$2\n";
                    }
                else { print CONF $_; }
                $ok = ( /^\}/ )? 3 : 2;
    	        }
    	    else { print CONF $_; }
            $ok=2 if /^SERVICES \{/;
            }
        close CONF;
        &webmin_log("change services in ".$config{cyrus_conf_path});
        }
	
	while (($k, $v)=each %in) { $imapParams{$k}=$v; } 
    checkSubParams('altnamespace','userprefix','sharedprefix');
    checkSubParams('virtdomains','defaultdomain');	
# write config file removing default parameters
	open CONF, ">".$config{imapd_conf_path};
	while (($k,$v)=each %imapParams)
		{
        if ($v ne "" && $v ne $defaults{$k})
		    { print CONF "$k: $v\n" ; }
		}
	close CONF;
	$restart=1;
	&webmin_log("change parameters in ".$config{imapd_conf_path});
	}

# parameter configuration form

print "<FORM METHOD=POST onSubmit=convquota(this)>\n<TABLE CELLPADDING=2 BORDER=1>";
# to force virtdomains=0 and sasl_mech_list=PLAIN
#print "<INPUT TYPE=HIDDEN NAME=virtdomains VALUE=0>
print "<INPUT TYPE=HIDDEN NAME=sasl_mech_list VALUE=PLAIN>\n";
# ....
foreach $name (@aParams)
	{
	if ($imapParams{$name}) { $value=$imapParams{$name} }
	elsif ($locals{$name}) { $value=$locals{$name} }
	else { $value=$defaults{$name} }
	print "<TR $cb>\n<TD>", $text{$name}, "</TD>\n<TD>";
	$type=$types{$name};
	$size=($sizes{$name})? $sizes{$name} : 25;
    $js=($jsChecks{$name})? " ".$jsChecks{$name} : "";
    $unit=($units{$name})? $units{$name} : "";
	SWITCH:
		{
		if ($type eq "F")
			{ 
			&$name($value); 
			last SWITCH;
			}
		if ($type eq "T")
			{
			print &ui_textbox($name, $value, $size.$js);
			print $unit if $unit;
			last SWITCH;
			}
		if ($type eq "L")
			{
			my_radio($name, $value);
			last SWITCH;
			}
		if ($type eq "Y")
			{
		    $value = 1 if $value eq 'true' or $value eq 'yes';
		    $value = 0 if $value eq 'false' or $value eq 'no';
			print &ui_yesno_radio($name, $value);
			last SWITCH;
			}
		print &ui_opt_textbox($name, $value, 25, $default{$name}, $text{'custom'});
		}
	print "</TD>\n</TR> ";
	}
print '</TABLE><INPUT TYPE=SUBMIT NAME=update VALUE="', $text{'update'}, '">';
print '&nbsp;&nbsp;<INPUT TYPE=SUBMIT NAME=apply VALUE="', $text{'apply'}, '">' if $restart;
print "</FORM>";

$onlynum=$text{numbers_only};
$betwnum=$text{numbers_between};

print "\n<SCRIPT>\nf=document.forms[0];\n";
while (($opt,$text)=each %hDisable)
    { print "if (f.".$opt."[0].checked) f.$text.disabled=true;\n"; }

print <<JS;

function IsNum(v)
{ 
if (v.value && isNaN(v.value))
    {
    alert("$onlynum.");
    v.value="";
    v.focus();
    return false;
    }
else return true;
}

function IsInt(v)
{ if (IsNum(v)) v.value=parseInt(v.value); }

function Between(v,min,max)
{
if (IsNum(v) && (parseInt(v.value)<min || parseInt(v.value)>max))
        {
        alert("$betwnum "+min+" - "+max+".");
        v.value=min;
        return false;
        }
else return true;
}

function convquota(f)
{
pow=f.autocreatequota_units.selectedIndex;
pow=f.autocreatequota_units.options[pow].value/1024.0;
f.autocreatequota.value=f.autocreatequota.value*pow;
}
</SCRIPT>
JS

&ui_print_footer("index.cgi", $text{'index_title'});


