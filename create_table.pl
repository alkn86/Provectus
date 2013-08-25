#!/usr/bin/perl -w
use strict;
use DBI;

my $dbh=DBI->connect( "DBI:mysql:database=customers", 'root', 'PerlStudent' )
	  or warn "Unable to connect to DB";	  

$dbh->do('use customers');
$dbh->do('drop table if exists `customer`');
$dbh->do('CREATE  TABLE `customer` (
  `customer_id` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `login` VARCHAR(50) NOT NULL ,
  `password` VARCHAR(80) NOT NULL ,
  `text_num` INT(64) NOT NULL DEFAULT 1 ,
  PRIMARY KEY (`customer_id`) ,  
  UNIQUE INDEX `login_UNIQUE` (`login` ASC))
ENGINE = MyISAM');
$dbh->do('drop table if exists `comments`');
$dbh->do('CREATE  TABLE `comments` (
  `name` VARCHAR(50) NOT NULL ,
  `comment` TEXT NOT NULL )
ENGINE = MyISAM');
$dbh->disconnect();
