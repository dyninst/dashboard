<%
# Display a summary row for a single run
#
# inputs:
#
#	`run` - A dict of 'run' information
#	`url` - An instance of `bottle.url`
#

if run is not None:

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

	<tr>
	<td align="center"><a href="{{ url('/details') }}/{{ run['runid'] }}">{{ run['runid'] }}</a></td>
	<td align="center">{{run['run_date']}}</td>
	<td align="center">{{run['arch']}}/{{run['vendor']}}</td>
	<td align="center">{{run['hostname']}}</td>
	<td align="center">{{run['compiler_name']}}</td>
	<td align="center">{{run['libc']}}</td>

%	bgcolor = get_status_color(run['dyninst_build_status'])
	<td align="center" bgcolor={{bgcolor}}>{{run['dyninst_build_status']}}</td>
	
%	bgcolor = get_status_color(run['tests_build_status'])
	<td align="center" bgcolor={{bgcolor}}>{{run['tests_build_status']}}</td>

%	# If the summary is a dictionary, then it contains the results
%	# If not, then 'summary' is a string describing why there are not results
%	if isinstance(run['summary'], dict):
		<td align="center">
%		for t in ('PASSED','FAILED','SKIPPED','CRASHED'):
			<a href="{{ url("/results") }}/{{ t }}/{{ str(run['runid'])  }}" title="{{ t }}">{{ str(run['summary'][t])  }}</a>
%		end
		({{ str(run['summary']['TOTAL']) }})
	    </td>
%	else:
    	<td align="center" bgcolor={{ get_status_color(run['summary']) }}>{{ run['summary'] }}</td>
%	end

% 	if str(run['regressions']).isdigit():
		<td align="center" bgcolor=#FA5858>
			<a href="{{ url('/regressions', id=run['runid']) }}">{{run['regressions']}}</a>
		</td>
% 	else:
%		bgcolor=get_status_color(run['regressions'])
		<td align="center" bgcolor={{bgcolor}}>{{run['regressions']}}</td>
% 	end
	
<%	for t in ('dyninst','testsuite'):
		branch = run['{0:s}_branch'.format(t)]
		commit = run['{0:s}_commit'.format(t)]
		link = 'https://github.com/dyninst/{0:s}/commit/{1:s}'.format(t, commit)
		if branch[0:2] == 'PR':
			# pull request branches have the for PRXXX
			link = 'https://github.com/dyninst/{0:s}/pull/{1:s}'.format(t, branch[2:])
		end
%>
		<td align="center">{{branch}}/<a href="{{link}}">{{commit[0:7]}}</a></td>
%	end
	<td align="center"><a href="{{ url('/logs') + '/' + run['upload_file'] }}">Download</a></td>
	</tr>
% end

