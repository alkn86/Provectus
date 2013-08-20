#!/usr/bin/perl -w
#!/usr/bin/env perl
use strict;
use warnings;
use CGI;
use DBI;
use CGI::Session;
use Digest::MD5 qw(md5_hex);

if ( $ENV{REQUEST_METHOD} eq 'GET' )
{
	my $co = new CGI;
	
	#if cookies already exists
	my $cookies_val = $co->cookie('CGISESSID')||undef;
	if($cookies_val){
		$co->redirect('viewer.cgi');
	}
	
	#
	print $co->header,
	  $co->start_html(
		-title   => 'Log in',
		-author  => 'Alex',
		-BGCOLOR => 'white',
		-LINK    => 'blue'
	  ),
	  $co->h2('Login please'),
	  $co->p(
'If you haven\'t login, type new and system will register you automaticly'
	  ), $co->hr,
	  $co->startform(
		-method => "POST",
		-action => 'login.cgi'
	  ),
	  $co->textfield(
		-name        => 'login',
		-placeholder => 'Your login'
	  ),
	  $co->p,
	  $co->password_field(
		-name        => 'password',
		-size        => 50,
		-maxlength   => 80,
		-placeholder => 'Type your password'
	  ),
	  $co->p, $co->submit( -label => 'Log in' ),
	  $co->checkbox(
		-name    => 'use_cookies',
		-label   => 'Use cookies',
		-value   => 'On',
		-checked => 1
	  ),
	  $co->endform(), $co->end_html;
}

if ( $ENV{REQUEST_METHOD} eq 'POST' )
{

	my $dbh = DBI->connect( "DBI:mysql:database=customers", 'root', 'PerlStudent' ) or die "Unable to connect to DB";
	my $co        = new CGI;
	my $login     = $co->param('login');
	my $password  = $co->param('password');
	my $check_box = $co->param('use_cookies');
	my $sth       =	  $dbh->prepare('select password from customer where login = ?');
	$sth->execute($login);
	my @res = $sth->fetchrow_array;
	if (@res)
	{ #login exists
		my $pass_checksum = shift(@res);
		my $input_pass_checksum = md5_hex($password);
		if($pass_checksum==$input_pass_checksum)
		{ 
			#password matched
			my $id_db_hendler = $dbh->prepare('select customer_id from `customer` where login = ?');
			$id_db_hendler->execute($login);
			my @cust_line = $id_db_hendler->fetchrow_array;
			my $user_id = shift (@cust_line);
			my $session = new CGI::Session( "driver:File", undef, { Directory => "/tmp" } );
		 	$session->param( "user_id", $user_id );		
		 	my $sid = $session->id();
		 	if ( $check_box eq 'On' ) #With Cookies
		 	{
				my $cookie = $co->cookie( CGISESSID => $sid );
		 		print $co->header( -cookie => $cookie ), $co->start_html,
				  $co->h1("$user_id"), $co->redirect('viewer.cgi'), $co->end_html;
	 		}
	 			else  #Without cookies (using querystring)
	 			{
	 				$co->redirect("viewer.cgi?ssid=$sid");
	 			}
		}

		else
		{ # password doesn't matched
			print $co->header, $co->start_html;
		 	print $co->p("Wrong password :((");		 	
			print $co->p($co->a({href=>'login.cgi'},'Go Back'));
			print $co->end_html;
		}
	}
	else #new account
	{
		my $new_password_checksum = md5_hex($password);
		if($password&&$login)
		{
			$dbh->do('Insert into `customer` (`login`,`password`) values (?,?)',{},$login,$new_password_checksum);
			print $co->header, $co->start_html;
			print $co->p("New account created, please log in");		 	
			print $co->p($co->a({href=>'login.cgi'},'Log In'));
			print $co->end_html;
		}
		else
		{
			print $co->header, $co->start_html;
			print $co->p("Fields can't be empty");		 	
			print $co->p($co->a({href=>'login.cgi'},'Go back'));
			print $co->end_html;
		}	
	}
	
	$sth->finish();
	$dbh->disconnect();

}
