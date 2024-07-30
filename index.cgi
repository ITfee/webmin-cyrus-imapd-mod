#!/usr/bin/perl
#
# Webmin module for Cyrus IMAPd
# Copyright (C) 2005
# Roberto Tecchio <roberto@tecchio.net>
# http://www.tecchio.net/webmin/cyrus
# 
# HTML Layout based on IMAPd module written by Christian Schneider and Johannes Walch
# http://www.nwe.de/develop/imapadmin
#
# Mailboxes Tree javascript by TreeMenu (http://www.treemenu.net)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA 02111-1307, USA.
#
require './cyrus-lib.pl';
&ReadParse();

$title=$text{'index_title'};
$rpm=`rpm -q cyrus-imapd`;
@vers=split("-",$rpm);
$rpmh="Cyrus IMAP ".$vers[2] if $vers[2];

&ui_print_header(undef,$text{'index_title'}, undef, undef, 1, 1, 0, 
	"<a href=http://$HOMESITE/$HOMEPAGE target=_BLANK>$text{'homepage'}</a>",
	undef, undef, $rpmh);

perldeps("Cyrus::IMAP", "Tree::Simple", "Encode", "HTML::Entities");

&stop if $in{stop}; &start if $in{start}; 

if (&cyrus_connect())
	{
	my @icon_array=("images/config.gif", "images/partitions.gif", "images/mailbox.gif");
	my @link_array=("config.cgi","partitions.cgi", "mailbox.cgi");
	my @title_array=($text{config}, $text{partitions}, $text{mbox_tree});

	&icons_table(\@link_array,\@title_array,\@icon_array);

	print '<TABLE WIDTH=100%><TR><TD><form method=post>
	<input name=stop type=submit value="', $text{'stop_cyrus'}, '"></td>
	</form></TD>
	';
	}
else
	{
	print '<TABLE WIDTH=100%><TR><TD><FORM method=post>
    <input name=start type=submit value="', $text{'start_cyrus'}, '"></td>
	</form></TD>
	';
	}

print "<TD ALIGN=RIGHT><I>mod. ",$module_name, " ", $module_info{version}; 
if ($config{chkupdate})
	{
	&http_download($HOMESITE, 80, "/$HOMEPAGE/lastrelease.php", "/tmp/lastversion", \$errhttp);
	unless($errhttp)
		{
		$last=`cat /tmp/lastversion`;
		print " - <a href=http://$HOMESITE/$HOMEPAGE target=_BLANK>$text{'new_release'} $last</a>" if $last gt $module_info{version};
		unlink "/tmp/lastversion";
		}
	}
print "</I></TD></TR></TABLE>\n";

&ui_print_footer();