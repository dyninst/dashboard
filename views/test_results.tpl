<!DOCTYPE html>
<html>
<body>

% if results is None:
		<span>No results found</span>
% else:

	<span style="">Test results for</span>
	<br>
	<table border="1" style="margin-left:3%">
	<tr>
		<th>Date</th>
		<th>Arch</th>
		<th>Host</th>
		<th>libc</th>
		<th>Dyninst</th>
		<th>Testsuite</th>
		<th>Log Files</th>
	</tr>
	<tr>
		<td align="center">{{results['run']['run_date']}}</td>
		<td align="center">{{results['run']['arch']}}/{{results['run']['vendor']}}</td>
		<td align="center">{{results['run']['hostname']}}</td>
		<td align="center">{{results['run']['libc']}}</td>
	
	<%	for t in ('dyninst','testsuite'):
			branch = results['run']['{0:s}_branch'.format(t)]
			commit = results['run']['{0:s}_commit'.format(t)]
			link = 'https://github.com/dyninst/{0:s}/commit/{1:s}'.format(t, commit)
			if branch[0:2] == 'PR':
				# pull request branches have the for PRXXX
				link = 'https://github.com/dyninst/{0:s}/pull/{1:s}'.format(t, branch[2:])
	   		end
	%>
		<td align="center">{{branch}}/<a href="{{link}}">{{commit[0:7]}}</a></td>
	%	end
		<td align="center"><a href="{{ url('/logs') + '/' + results['run']['upload_file'] }}">Download</a></td>
	</tr>
	</table>
	
	<br>
	<span style="font-size:25px;">{{results['result_type'] + ' Tests'}}</span>
	<br>
	
	% if results['results'] is not None:
		<table border="1" style="margin-left:5%">
		<tr>
			<th>Test Name</th>
			<th>Compiler</th>
			<th>Optimization</th>
			<th>ABI</th>
			<th>Mode</th>
			<th>Threading</th>
			<th>Linkage</th>
			<th>PIC</th>
			<th>Reason</th>
		</tr>
		% for r in results['results']:
			<tr>
				<td align="center">{{r['test_name']}}</td>
				<td align="center">{{r['compiler']}}</td>
				<td align="center">{{r['optimization']}}</td>
				<td align="center">{{r['abi']}}</td>
				<td align="center">{{r['mode']}}</td>
				<td align="center">{{r['threading']}}</td>
				<td align="center">{{r['link']}}</td>
				<td align="center">{{r['pic']}}</td>
				<td align="center">{{r['reason']}}</td>
			</tr>
		% end
		</table>
		<br><br>
	% else:
		<span style="margin-left:5%;font-size:150%;">No results found</span>
	% end
%end
</body>
</html>
