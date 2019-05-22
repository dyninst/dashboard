<!DOCTYPE html>
<html>
<body>

<table border="1">

<tr>
<th>Date</th>
<th>Arch</th>
<th>Host</th>
<th>libc</th>
<th>Build Status</th>
<th><span title="Pass/Fail/Skip/Crash (Total)">Results</span></th>
<th>Regressions</th>
<th>Dyninst</th>
<th>Testsuite</th>
</tr>

% for r in runs:
	<tr>
	<td align="center">{{r['date']}}</td>
	<td align="center">{{r['arch']}}/{{r['vendor']}}</td>
	<td align="center">{{r['hostname']}}</td>
	<td align="center">{{r['libc']}}</td>
	<%
	if r['build_status'] == 'OK':
		bgcolor='#58FA58'
	else:
		bgcolor='#FA5858'
	end
	%>
	<td align="center" bgcolor={{bgcolor}}>{{r['build_status']}}</td>
	<td align="center">{{r['summary']}}</td>

% 	if r['regressions'] == 'Unknown':
		<td align="center" bgcolor=#ECCB39>{{r['regressions']}}</td>
%	elif r['regressions'] == 'none':
		<td align="center" bgcolor=#58FA58>{{r['regressions']}}</td>
% 	else:
		<td align="center" bgcolor=#FA5858>
			<a href="/regressions?id={{r['runid']}}">{{r['regressions']}}</a>
		</td>
% 	end
	
	<td align="center">{{r['dyninst_branch'] + ' / ' + r['dyninst_commit'][0:7]}}</td>
	<td align="center">{{r['testsuite_branch'] + ' / ' + r['testsuite_commit'][0:7]}}</td>
	</tr>
%end

</table>

<br><br>
<a href="/upload">Upload a new run</a>
</body>
</html>
