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
<th>Log Files</th>
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
			<a href="{{base_url}}/regressions?id={{r['runid']}}">{{r['regressions']}}</a>
		</td>
% 	end
	
<%	for t in ('dyninst','testsuite'):
		branch = r['{0:s}_branch'.format(t)]
		commit = r['{0:s}_commit'.format(t)]
		link = 'https://github.com/dyninst/{0:s}/commit/{1:s}'.format(t, commit)
		if branch[0:2] == 'PR':
			# pull request branches have the for PRXXX
			link = 'https://github.com/dyninst/{0:s}/pull/{1:s}'.format(t, branch[2:])
		end
%>
		<td align="center">{{branch}}/<a href="{{link}}">{{commit[0:7]}}</a></td>
%	end
	<td align="center"><a href="{{base_url}}/logs/{{r['upload_file']}}">Download</a></td>
	</tr>
% end
</table>

<br><br>
<a href="{{base_url}}/upload">Upload a new run</a>
</body>
</html>
