#!/usr/bin/perl
# display the mailboxes tree

require './functions-lib.pl';

use CGI; $q=new CGI; 
iframe_header($cb);

# Fetch mailboxes
my $cyrus = &cyrus_connect();
@list = $cyrus->list("*"); # Fetch all mailboxes below the current path
%mboxes=();

get_config();
if ($imapParams{virtdomains}!=0) { require "./tree_virtdoms.pl"; }
else { require "tree.pl";  }

print $q->end_html();