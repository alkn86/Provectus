#!/usr/bin/perl -w 
use strict;
use warnings;

use CGI;

sub openWrite {
	my $filename = shift;
	my $name     = shift;
	my $comment  = shift;
	my $co       = new CGI;	
	my $time     = localtime;
	if ( $name && $comment ) {
		open( FH, ">>", $filename ) or die "OpenErite Error";
		print FH $co->hr, $co->p, "$name wrote at $time:", $co->p,$co->em("$comment"),
		  $co->p;
		close(FH);
	}
}

sub readComment {
	my $filename = shift;
	if ( -e $filename ) {
		open( FH, "<", $filename ) or die "Can't open file";
		my $result = <FH>;
		close(FH);
		return $result;
	}
	return;

}
if ( $ENV{REQUEST_METHOD} eq 'POST' ) {
	my $co      = new CGI;
	my $name    = $co->param('visitor_name');
	my $comment = $co->param('comment');
	if ( $name && $comment ) {
		&openWrite( "comments.htm", $name, $comment );
		$name = undef;
		$comment = undef;
	}
	print $co->redirect('comment.cgi');
	

}

if ( $ENV{REQUEST_METHOD} eq 'GET' ) {

	my $co = new CGI;
	print $co->header(),
	  $co->start_html(
		-title   => 'Comments',
		-author  => 'Alex',
		-BGCOLOR => 'white',
		-LINK    => 'blue'
	  ),
	  $co->h1("Leave your comment please!"),
	  $co->startform(
		-method => 'POST',
		-action => 'comment.cgi'
	  ),

	  $co->textfield(
		-name        => 'visitor_name',
		-placeholder => "Write your name here",
		-value       => ""
	  ),
	  $co->p,

	  $co->textarea(
		-name        => 'comment',
		-placeholder => 'Write your opinion here',
		-rows        => 10,
		-columns     => 60,
		-value       => ""
	  ),
	  $co->p, $co->submit, $co->reset(), &readComment("comments.htm"),
	  $co->endform(), $co->end_html();

}
