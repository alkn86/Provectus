#!/usr/bin/perl -w
#!/usr/bin/env perl
use strict;
use warnings;
use CGI;
use DBI;
use CGI::Session;
use Digest::MD5 qw(md5_hex);

my $msg = "If you haven't login, type new and system will register you automaticly";
my $co = new CGI;
	
#if cookies already exists
my $cookies_val = $co->cookie('CGISESSID')||undef;
if($cookies_val){
	$co->redirect('viewer.cgi');
}

if ( $ENV{REQUEST_METHOD} eq 'POST' )
{

	my $dbh = DBI->connect( "DBI:mysql:database=customers", 'root', 'PerlStudent' ) or die "Unable to connect to DB";	
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
		 	if ( $check_box eq 'On' ){	
		 		#With Cookies
				my $cookie = $co->cookie( CGISESSID => $sid );
		 		print $co->header( -cookie => $cookie ), $co->start_html,
				  $co->h1("$user_id"), $co->redirect('viewer.cgi'), $co->end_html;
	 		}
	 			else{  #Without cookies (using querystring)
	 			
	 				$co->redirect("viewer.cgi?ssid=$sid");
	 			}
		}

		else
		{ # password doesn't matched
			$msg = '<font color="#CC0000"> Wrong password! </font>';
		}
	}
	else #new account
	{
		my $new_password_checksum = md5_hex($password);
		if($password&&$login)
		{
			$dbh->do('Insert into `customer` (`login`,`password`) values (?,?)',{},$login,$new_password_checksum);
			$msg = '<font color="#228B22">New account created, please log in</font>';
		}
		else
		{
			$msg = '<font color="#CC0000">Error: Fields cant be empty! </font>';
		}	
	}
	
	$sth->finish();
	$dbh->disconnect();

}	
# HTML
print $co->header,
$co->start_html(
	-title   => 'Log in',
	-author  => 'Alex',
	-BGCOLOR => 'white',
	-LINK    => 'blue'
	  ),
qq|<h2>Login please</h2><hr /><p>$msg</p>|,
qq|<form method="POST" action="login.cgi" enctype="application/x-www-form-urlencoded" name="login">|,
qq|<input type="text" name="login"  placeholder="Your login" /><p />|,
qq|<input type="password" name="password"  size="50" maxlength="80" placeholder="Type your password" /><p /><hr />|,
qq|<p /><input type="submit" name=".submit" value="Log in" />|,
qq|<label><input type="checkbox" name="use_cookies" value="On" checked="checked" />Use cookies</label>|,
qq|<div><input type="hidden" name=".cgifields" value="use_cookies"  /></div></form>|,
$co->end_html;