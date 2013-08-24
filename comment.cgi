#!/usr/bin/perl -w 
use strict;
use CGI;
my $co = new CGI;
use DBI;

my $dbh = DBI->connect( "DBI:mysql:database=customers", 'root', 'PerlStudent' ) or die "Unable to connect to DB";

if ( $ENV{'REQUEST_METHOD'} eq 'POST' ) {	
	my $name    = $co->param('visitor_name');
	my $comment = $co->param('comment');
	my $time = localtime;	
	my $comment_html = qq|<hr /><p><font color="#008B8B">$name</font> wrote at $time :</p><p><em>$comment</em></p>|;	
	if ( $name && $comment ) {
			$dbh->do('Insert into `comments` (`name`,`comment`) values (?,?)',{},$name,$comment_html) or warn 'BAD COMMAND';
	}
}
	print $co->header(),
	  $co->start_html(
		-title   => 'Comments',
		-author  => 'Alex',
		-BGCOLOR => 'white',
		-LINK    => 'blue'
	  ),
	  qq|<h1>Leave your comment please!</h1>|,
	  qq|<form method="POST" action="comment.cgi" enctype="application/x-www-form-urlencoded" name="comment">|,
	  qq|<input type="text" name="visitor_name"  placeholder="Write your name here" /><p />|,
	  qq|<textarea name="comment"  rows="10" cols="60" placeholder="Write your opinion here"></textarea><p />|.
	  qq|<input type="submit" name=".submit" />|,
	  qq|</form>|;	  
	  my $sth= $dbh->prepare('Select `comment` from `comments`');
	  $sth->execute();
	  while(my @res =$sth->fetchrow_array()){
	  	print @res;
	  }
	  $sth->finish();
	  print  $co->endform(), $co->end_html();
	  $dbh->disconnect();