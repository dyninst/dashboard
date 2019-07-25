create table link_type("name" varchar(12));
insert into link_type(name) values('dynamic');
insert into link_type(name) values('static');

create table status("name" varchar(8));
insert into status(name) values('FAILED');
insert into status(name) values('CRASHED');
insert into status(name) values('SKIPPED');
insert into status(name) values('PASSED');

create table mode("name" varchar(12));
insert into mode(name) values('attach');
insert into mode(name) values('create');
insert into mode(name) values('disk');
insert into mode(name) values('rewriter');

create table run(
	"id" INTEGER NOT NULL PRIMARY KEY,
	"arch" TEXT,
	"vendor" TEXT,
	"os" TEXT,
	"kernel" TEXT,
	"kernel_version" TEXT,
	"libc" TEXT,
	"hostname" TEXT,
	"dyninst_build_status" TEXT,
	"tests_build_status" TEXT,
	"tests_run_status" TEXT,
	"run_date" DATE,
	"upload_date" DATE,
	"dyninst_commit" TEXT,
	"dyninst_branch" TEXT,
	"testsuite_commit" TEXT,
	"testsuite_branch" TEXT,
	"upload_file" TEXT,
	"compiler_name" TEXT
);

CREATE TABLE compiler (
	"id" INTEGER NOT NULL PRIMARY KEY,
	"name" TEXT,
	"path" TEXT,
	"version" TEXT,
	"language" TEXT
);

CREATE TABLE run_compiler (
	"id" INTEGER NOT NULL PRIMARY KEY,
	"runid" INTEGER NOT NULL,
	"compilerid" INTEGER NOT NULL,
	"target" TEXT,
	FOREIGN KEY(runid) references run(id),
	FOREIGN KEY(compilerid) references compiler(id)
);

create table test_result(
	"resultid" INTEGER NOT NULL PRIMARY KEY,
	"runid" INTEGER NOT NULL,
	"test_name" TEXT,
	"compiler" TEXT,
	"optimization" TEXT,
	"abi" TEXT,
	"mode" TEXT,
	"threading" TEXT,
	"link" TEXT,
	"pic" TEXT,
	"result" TEXT,
	"reason" TEXT,
	FOREIGN KEY(runid) references run(id)
);

create view run_v as
select
    id,
    arch,
    vendor,
    os,
    kernel,
    kernel_version,
    libc,
    hostname,
    dyninst_build_status,
    tests_build_status,
    tests_run_status,
    datetime(run_date) as run_date,
    datetime(upload_date) as upload_date,
    dyninst_commit,
    dyninst_branch,
    testsuite_commit,
    testsuite_branch,
    upload_file,
    compiler_name
from run;

CREATE TABLE auth_token (
	"id" INTEGER NOT NULL PRIMARY KEY,
	"token" TEXT,
	"hostname" TEXT
);

insert into auth_token("hostname","token") values ("cayenne.cs.wisc.edu","ec2798c1fb37cce8d95d8e1d558bd519");
insert into auth_token("hostname","token") values ("zeroah.cs.wisc.edu","b2f3bf6a6f317cde6b71547db132e797");
insert into auth_token("hostname","token") values ("leela.cs.wisc.edu","1fa510720181141c3280b240094371d6");
insert into auth_token("hostname","token") values ("zatar.cs.wisc.edu","d1549a402ea3fc0facedd5568230ba78");
insert into auth_token("hostname","token") values ("ray.llnl.gov","14c2751e1fabf1a0954d4c14b5b8f896");
insert into auth_token("hostname","token") values ("lassen.llnl.gov","3bd2daf2deca6d1fcbdc65116340b977");
insert into auth_token("hostname","token") values ("quartz.llnl.gov","cd25856ec3b601bf1ad0e5efc9170247");
insert into auth_token("hostname","token") values ("GalacticCentralPoint","14bb4ad2d33e1fa292c0561b7dad8232");
insert into auth_token("hostname","token") values ("cori","2af8d40c965d41781327a4f97fe6452d");
