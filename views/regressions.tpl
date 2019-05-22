<!DOCTYPE html>
<html>
<body>

<span style="">Regressions for</span>

% r = regs['base_commit']
	<table border="1">
	<tr>
		<th>Date</th>
		<th>Arch</th>
		<th>Host</th>
		<th>libc</th>
		<th>Dyninst</th>
		<th>Testsuite</th>
	</tr>
	<tr>
		<td align="center">{{r['date']}}</td>
		<td align="center">{{r['arch']}}/{{r['vendor']}}</td>
		<td align="center">{{r['hostname']}}</td>
		<td align="center">{{r['libc']}}</td>
		<td align="center">{{r['dyninst_branch'] + ' / ' + r['dyninst_commit'][0:7]}}</td>
		<td align="center">{{r['testsuite_branch'] + ' / ' + r['testsuite_commit'][0:7]}}</td>
	</tr>
	</table>

% r = regs['against_host']['run']
<br><br>
<span style="">against the most recent run on {{r['hostname']}}</span>
<br><br> 
	<table border="1">
	<tr>
		<th>Date</th>
		<th>Arch</th>
		<th>Host</th>
		<th>libc</th>
		<th>Dyninst</th>
		<th>Testsuite</th>
	</tr>
	<tr>
		<td align="center">{{r['date']}}</td>
		<td align="center">{{r['arch']}}/{{r['vendor']}}</td>
		<td align="center">{{r['hostname']}}</td>
		<td align="center">{{r['libc']}}</td>
		<td align="center">{{r['dyninst_branch'] + ' / ' + r['dyninst_commit'][0:7]}}</td>
		<td align="center">{{r['testsuite_branch'] + ' / ' + r['testsuite_commit'][0:7]}}</td>
	</tr>
	</table>

% # ------ Regressions -------
<br><br>
	<table border="1">
	<tr>
		<th>Test Name</th>
		<th>Compiler</th>
		<th>Optimization</th>
		<th>ABI</th>
		<th>Mode</th>
		<th>Threading</th>
		<th>Linkage</th>
		<th>PIC</th>
		<th>Result</th>
		<th>Reason</th>
	</tr>

%	for r in regs['against_host']['regressions']:
		<tr>
			<td align="center">{{r['test_name']}}</td>
			<td align="center">{{r['compiler']}}</td>
			<td align="center">{{r['optimization']}}</td>
			<td align="center">{{r['abi']}}</td>
			<td align="center">{{r['mode']}}</td>
			<td align="center">{{r['threading']}}</td>
			<td align="center">{{r['link']}}</td>
			<td align="center">{{r['pic']}}</td>
			<td align="left">{{r['previous_result']}} -> {{r['current_result']}}</td>
			<td align="center">{{r['reason']}}</td>
		</tr>
%	end
	</table>

</body>
</html>
