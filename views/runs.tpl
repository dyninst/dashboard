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
<th><span title="Pass/Fail/Skip/Crash (Total)">Test Results</span></th>
<th>Regressions</th>
<th>Dyninst</th>
<th>Testsuite</th>
</tr>

<%
	status_colors = {
		'OK':'#58FA58',
		'FAILED':'#FA5858',
		'Unknown':'#ECCB39',
		'none':'#58FA58'
	}
%>

% for r in runs:
	<tr>
	<td align="center">{{r['date']}}</td>
	<td align="center">{{r['arch']}}/{{r['vendor']}}</td>
	<td align="center">{{r['hostname']}}</td>
	<td align="center">{{r['libc']}}</td>

%	bgcolor = status_colors[r['build_status']]
	<td align="center" bgcolor={{bgcolor}}>{{r['build_status']}}</td>

<%	if r['summary'] in status_colors:
		bgcolor = status_colors[r['summary']]
	else:
		bgcolor = '#FFFFFF'
	end
%>
	<td align="center" bgcolor={{bgcolor}}>{{r['summary']}}</td>

% 	if r['regressions'] in status_colors:
%		bgcolor=status_colors[r['regressions']]
		<td align="center" bgcolor={{bgcolor}}>{{r['regressions']}}</td>
% 	else:
		<td align="center" bgcolor=#FA5858>
			<a href="/regressions?id={{r['runid']}}">{{r['regressions']}}</a>
		</td>
% 	end
	
	<td align="center">{{r['dyninst_branch'] + ' / ' + r['dyninst_commit'][0:7]}}</td>
	<td align="center">{{r['testsuite_branch'] + ' / ' + r['testsuite_commit'][0:7]}}</td>
	</tr>
% end

</table>

<br><br>
<a href="/upload">Upload a new run</a>
</body>
</html>
