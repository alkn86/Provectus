#!/usr/bin/perl -w
use strict;
use warnings;

use CGI;

sub check_int {
	my $check_int = int( rand(10) );
	if ( $check_int % 2 == 0 ) { return 1; }
	else { return 0; }
}

sub check_str {
	my $check_int = int( rand(10) );
	if ( $check_int % 2 == 0 ) { return 'I am not a spam bot'; }
	else { return 'I am a spam bot'; }
}
if ( $ENV{REQUEST_METHOD} eq 'GET' ) {
	my $co    = new CGI;
	my $label = &check_str;
	print $co->header(),
	  $co->start_html(
		-title   => 'Mail Sending',
		-author  => 'Alex',
		-BGCOLOR => 'white',
		-LINK    => 'blue'
	  ),
	  $co->center( $co->h1('Send us a message') ), $co->hr, $co->p,
	  $co->startform(
		-method => 'POST',
		-action => 'mail.cgi'
	  ),
	  $co->p("Your e-mail:"),
	  $co->textfield(
		-name        => 'e-mail',
		-placeholder => "Write your e-mail here"
	  ),
	  $co->p("Subject:"),
	  $co->textfield(
		-name        => 'subject',
		-placeholder => 'Write subject here'
	  ),

	  $co->p("Message:"),
	  $co->textarea(
		-name        => 'message',
		-placeholder => 'Write your message here',
		-rows        => 10,
		-columns     => 60
	  ),
	  $co->hidden( -name => 'label', -default => $label ), $co->p,
	  $co->submit( -name => 'Send' ),

	  $co->checkbox(
		-name    => 'human_check',
		-label   => $label,
		-value   => 'On',
		-checked => &check_int
	  ),
	  $co->endform, $co->end_html;
}
else {
	my $co = new CGI;
	$" = ' / ';
	my @params      = $co->param;
	my $mail_from   = $co->param('e-mail');
	my $subject     = $co->param('subject');
	my $message     = $co->param('message');
	my $check_label = $co->param('label');
	my $check_box   = $co->param('human_check');
	my $error       = '';

	if (   ( ( $check_label eq 'I am not a spam bot' ) && ( $check_box eq '' ) )
		|| ( ( $check_label eq 'I am a spam bot' ) && ( $check_box eq 'On' ) ) )
	{
		$error .= "It seems like you are a spam bot;)" . "\n";
	}
	unless ( $mail_from =~ m/^(\w+[\.\-]?)+@(\w+)(\.\w+)+/ ) {
		$error .=
		  "Incorrect e-mail, or your e-mail domain is not supported. " . "\n";
	}
	unless ($subject) {
		$error .= "Subject can't be empty. " . "\n";
	}

	unless ($error) {
		print $co->header,
		  $co->start_html(
			-title   => 'Mail Sending',
			-author  => 'Alex',
			-BGCOLOR => 'white',
			-LINK    => 'blue'
		  );
		$mail_from =~ s/@/\@/;
		$message   =~ s/</&lt/;
		open( MAIL, "| /usr/lib/sendmail -t " );

		print MAIL "To: student\@perlstudent.tm.local\n";
		print MAIL "From: $mail_from\n";
		print MAIL "Subject: $subject\n\n";
		print MAIL "$message";
		close(MAIL) or warn "message wasn't sent\n" ;
		print $co->p("Thank you for message! You always can ".$co->a( { href => 'mail.cgi' }, 'write another one;)' )),		  
		  $co->end_html;
	}
	else {
		print $co->header;
		print $co->start_html(
			-title   => 'Mail Sending Error',
			-author  => 'Alex',
			-BGCOLOR => 'white',
			-LINK    => 'blue'
		  ),
		  $co->p("$error"), $co->p, $co->a( { href => 'mail.cgi' }, 'Go back' ),
		  $co->end_html;
	}

}
