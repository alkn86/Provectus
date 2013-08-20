#!/usr/bin/perl -w
use strict;

use CGI;
use CGI::Session;
use LWP::Simple;
use DBI;

my $dbh =
	  DBI->connect( "DBI:mysql:database=customers", 'root', 'PerlStudent' )
	  or die "Unable to connect to DB";

my $co = new CGI;
my $sid = $co->cookie('CGISESSID') || $co->url_param('ssid') ||$co->param('sid')|| undef;	
my $session = new CGI::Session( undef, $sid, { Directory => '/tmp' } );
my $user_id = $session->param("user_id")||undef;
my $current_quote = $session->param("current_quote")||$co->param("current_quote")||undef;

if ( $ENV{REQUEST_METHOD} eq 'POST' ) #Хранить номер статьи в сессии ,открывать из базы только при отсутствии сессии!!!!!!!!!!!!!!
{
			
	
	my $isNext = $co->param("next")||undef;	

	
	if($isNext)
	{
		$current_quote+=1;
		$session->param('current_quote',$current_quote);
		$dbh->do('update `customer` set text_num = ? where customer_id = ?',{},$current_quote,$user_id);
		$dbh->disconnect;			
		unless($co->cookie('CGISESSID')){$co->redirect("viewer.cgi?ssid=$sid");}
		else{$co->redirect("viewer.cgi");}			
	}

 else
	{	
	my $cookie = $co->cookie( CGISESSID => "" );
	print $co->header( -cookie => $cookie ), $co->start_html, $co->end_html;
	my $session = new CGI::Session( undef, $sid, { Directory => '/tmp' } );
	$session->delete();
	$co->redirect('login.cgi');
	}
}

else{


	

	
	
	unless ($user_id) { $session->delete(); $co->redirect('login.cgi'); }
	
	#RECEIVE THE QUOTE
	unless($current_quote)
	{
	my $sth = $dbh->prepare('Select text_num from `customer` where customer_id = ?');
	$sth->execute($user_id);
	my @query_result = $sth->fetchrow_array();
	$current_quote = shift(@query_result);
	$sth->finish;	
	$dbh->disconnect();
	$session->param("current_quote",$current_quote);
	}
	
	
	my $content = get("http://bash.org/?$current_quote");
	$content =~ m#(<p class="qt">).+(</p>)#s;
	my $res = $&;
	unless ($res) 
		{
		my $temp = $current_quote;
		while ( $res eq "" ) 
			{
				$temp += 1;
				$content = get("http://bash.org/?$temp");
				$content =~ m#(<p class="qt">).+(</p>)#s;
				$res = $&;
			}
		$session->param("current_quote",$temp);		
	
		$current_quote =$temp;
		}

	#HTML
	my $temp = $session->param('current_quote');
	print $co->header,
	  $co->start_html(
		-title   => 'Viewer',
		-author  => 'Alex',
		-BGCOLOR => 'white',
		-LINK    => 'blue'
	  ),$co->h2("Viewer"),
	  $co->hr,$co->p, $res,$co->p,
	   #form for next
	  $co->startform(
	  	-name => 'next',
	  	-method => 'POST',
	  	-action => 'viewer.cgi'
	  	),
	  $co->hidden(-name=>"next", -default => '1'), 
	  $co->hidden(
		-name    => "sid",
		-default => $sid
		),
	  $co->hr,
	  $co->hidden(-name =>'current_quote', -default =>$current_quote),
	  ,$co->submit( -label=>"Next" ),
	  $co->endform,$co->p(),
	  #Form for logout
	  $co->startform(
	  	-name=> 'logout',
		-method => 'POST',
		-action => 'viewer.cgi'
	  ),
	  $co->hidden(
		-name    => "sid",
		-default => $sid
	  ),
	  $co->submit( -label=>'Log out'  ),
	  $co->endform,
	  $co->end_html;
}


