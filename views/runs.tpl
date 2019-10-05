<!DOCTYPE html>
<html>
<body>

% if len(runs) == 0:
		<span>No runs found</span>
% else:

	<table border="1">
	
	<tr>
	<th>Date</th>
	<th>Arch</th>
	<th>Host</th>
	<th>Compiler Name</th>
	<th>libc</th>
	<th>Dyninst Build</th>
	<th>Tests Build</th>
	<th>Test Results</th>
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
		
		def get_status_color(status, default_color=''):
			if status in status_colors:
				return status_colors[status]
			else:
				return default_color
			end
		end
	%>
	
	% for r in runs:
		<tr>
		<td align="center">{{r['run_date']}}</td>
		<td align="center">{{r['arch']}}/{{r['vendor']}}</td>
		<td align="center">{{r['hostname']}}</td>
		<td align="center">{{r['compiler_name']}}</td>
		<td align="center">{{r['libc']}}</td>
	
	%	bgcolor = get_status_color(r['dyninst_build_status'])
		<td align="center" bgcolor={{bgcolor}}>{{r['dyninst_build_status']}}</td>
		
	%	bgcolor = get_status_color(r['tests_build_status'])
		<td align="center" bgcolor={{bgcolor}}>{{r['tests_build_status']}}</td>
	
	%	# If the summary is a dictionary, then it contains the results
	%	# If not, then 'summary' is a string describing why there are not results
	%	if isinstance(r['summary'], dict):
			<td align="center">
	%		for t in ('PASSED','FAILED','SKIPPED','CRASHED'):
				<a href="{{ url("/results") }}/{{ t }}/{{ str(r['runid'])  }}" title="{{ t }}">{{ str(r['summary'][t])  }}</a>
	%		end
			({{ str(r['summary']['TOTAL']) }})
		    </td>
	%	else:
	    	<td align="center" bgcolor={{ get_status_color(r['summary']) }}>{{ r['summary'] }}</td>
	%	end
	
	% 	if str(r['regressions']).isdigit():
			<td align="center" bgcolor=#FA5858>
				<a href="{{ url('/regressions', id=r['runid']) }}">{{r['regressions']}}</a>
			</td>
	% 	else:
	%		bgcolor=get_status_color(r['regressions'])
			<td align="center" bgcolor={{bgcolor}}>{{r['regressions']}}</td>
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
		<td align="center"><a href="{{ url('/logs') + '/' + r['upload_file'] }}">Download</a></td>
		</tr>
	% end
	</table>
% end

</body>
</html>
