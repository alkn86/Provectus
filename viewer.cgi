#!/usr/bin/perl -w
use strict;
use CGI;
use CGI::Session;
use LWP::Simple;
use DBI;

my $dbh = DBI->connect( "DBI:mysql:database=customers", 'root', 'PerlStudent' )
  or die "Unable to connect to DB";

my $co  = new CGI;
my $sid = $co->cookie('CGISESSID')|| $co->url_param('ssid')|| $co->param('sid')|| undef;
my $session = new CGI::Session( undef, $sid, { Directory => '/tmp' } );
my $user_id = $session->param("user_id") || undef;
unless ($user_id) { $session->delete(); $co->redirect('login.cgi'); }
my $current_quote = $co->param("current_quote")||$session->param("current_quote")|| undef;
my $limit_quote = $session->param("limit_quote") || undef;

	unless ($limit_quote) {
		my $latest = get("http://www.bash.org/?latest");
		$latest =~ m@(<p class="quote">)(.+?)\#(\d+)(.+?)(</p>)@;	
		$session->param( "limit_quote", $3 );
		$limit_quote =$session->param('limit_quote');
	}

	unless ($current_quote) {
		my $sth = $dbh->prepare('Select text_num from `customer` where customer_id = ?');
		$sth->execute($user_id);
		my @query_result = $sth->fetchrow_array();
		$current_quote = shift(@query_result);
		$sth->finish;
		$dbh->disconnect();
		$session->param( "current_quote", $current_quote );
	}

	if ( $ENV{REQUEST_METHOD} eq 'POST' ) {

		my $isNext = $co->param("next") || undef;

			unless($isNext) {
			my $cookie = $co->cookie( CGISESSID => "" );
			print $co->header( -cookie => $cookie );
			 
			my $session =  new CGI::Session( undef, $sid, { Directory => '/tmp' } );
			$session->delete();
			$co->redirect('login.cgi');
		}
		else{
			$current_quote += 1;
			$session->param( 'current_quote', $current_quote );						
		}		
	}

	my $content = get("http://bash.org/?$current_quote");
	$content =~ m#(<p class="qt">).+?(</p>)#s;
	my $res = $&;
	unless ($res) {		
		while ( $res eq "" ) {
			$current_quote += 1;
			$content = get("http://bash.org/?$current_quote");
			$content =~ m#(<p class="qt">).+(</p>)#s;
			$res = $&;
		}
		$session->param( "current_quote", $current_quote );		
	}
	#HTML
	print $co->header,
	  $co->start_html(
		-title   => 'Viewer',
		-author  => 'Alex',
		-BGCOLOR => 'white',
		-LINK    => 'blue'
	  ),
	  qq|<h2>Viewer</h2><p>Current quote: $current_quote</p><hr />|, 
	  qq|$res|,
	  qq|<hr /><p>Quote limit is: $limit_quote</p>|,
	  #form for next button
	  qq|<form method="POST" action="viewer.cgi" enctype="application/x-www-form-urlencoded" name="next">|,
	  qq|<input type="hidden" name="next" value="1" override="1"  />|,
	  qq|<input type="hidden" name="current_quote" value="$current_quote" override="1"  />|,	  	  
	  qq|<input type="hidden" name="sid" value="$sid" override="1" />|;	  	 
	  print $co->submit(-label => "Next", -disabled => 'disabled', -autofocus=>'autofocus') if ( $current_quote >= $limit_quote );
	  print $co->submit(-label => "Next", -autofocus=>'autofocus') if ( $current_quote < $limit_quote );
	  print qq|</form>|;
	  print 
	  #Form for logout
	  qq|<form method="POST" action="viewer.cgi" enctype="application/x-www-form-urlencoded" name="logout">|,
	  qq|<input type="hidden" name="sid" value="$sid"  />|,	  
	  $co->submit( -label => 'Log out' ),	  
	  qq|</form>|,	  
	  $co->end_html;
	  $dbh->do('update `customer` set text_num = ? where customer_id = ?',{}, $current_quote, $user_id );
	  $dbh->disconnect;


