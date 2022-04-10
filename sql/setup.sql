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

CREATE TABLE regression_count (
	"id" INTEGER NOT NULL PRIMARY KEY,
	"cur_run" INTEGER NOT NULL,
	"prev_run" INTEGER NOT NULL,
	"cnt" INTEGER,
	FOREIGN KEY(cur_run) references run(id),
	FOREIGN KEY(prev_run) references run(id)
);
CREATE UNIQUE INDEX regression_count_unique ON regression_count(cur_run,prev_run); 

CREATE TABLE test_result_summary (
  "id" INTEGER NOT NULL PRIMARY KEY,
  "runid" INTEGER NOT NULL,
  "passed" INTEGER NOT NULL,
  "failed" INTEGER NOT NULL,
  "skipped" INTEGER NOT NULL,
  "crashed" INTEGER NOT NULL,
  "hanged" INTEGER NOT NULL,
  FOREIGN KEY(runid) REFERENCES run(id)
);
CREATE UNIQUE INDEX test_result_summary_unique ON test_result_summary(runid);
