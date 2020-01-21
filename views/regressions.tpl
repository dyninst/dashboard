<!DOCTYPE html>
<html>
<body>

<span style="">Regressions for</span>
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
	<td align="center">{{regs['base_commit']['run_date']}}</td>
	<td align="center">{{regs['base_commit']['arch']}}/{{regs['base_commit']['vendor']}}</td>
	<td align="center">{{regs['base_commit']['hostname']}}</td>
	<td align="center">{{regs['base_commit']['libc']}}</td>

<% for t in ('dyninst','testsuite'):
		branch = regs['base_commit']['{0:s}_branch'.format(t)]
		commit = regs['base_commit']['{0:s}_commit'.format(t)]
		link = 'https://github.com/dyninst/{0:s}/commit/{1:s}'.format(t, commit)
		if branch[0:2] == 'PR':
			# pull request branches have the for PRXXX
			link = 'https://github.com/dyninst/{0:s}/pull/{1:s}'.format(t, branch[2:])
		end
%>
		<td align="center">{{branch}}/<a href="{{link}}">{{commit[0:7]}}</a></td>
% end

	<td align="center"><a href="{{ url('/logs') + '/' + regs['base_commit']['upload_file'] }}">Download</a></td>
</tr>
</table>
<br>

%	if regs['type'] == 'arch':
		<span style="">against the most recent runs on hosts with architecture <b>{{regs['base_commit']['arch']}}</b></span>
%	elif regs['type'] == 'run':
		<span style="">against the single run </b></span>
%	elif regs['type'] == 'host':
		<span style="">against the most recent run on <b>{{regs['base_commit']['hostname']}}</b></span>
%	else:
		<span style="">Unknown type: This should not happen</b></span>
%	end

	% for res in regs['results']:
		<hr>
		<table border="1" style="margin-left:3%">
		<tr>
			<th>Host</th>
			<th>Date</th>
			<th>Vendor</th>
			<th>libc</th>
			<th>Dyninst</th>
			<th>Testsuite</th>
			<th>Log Files</th>
		</tr>
		<tr>
			<td align="center">{{res['run']['hostname']}}</td>
			<td align="center">{{res['run']['run_date']}}</td>
			<td align="center">{{res['run']['vendor']}}</td>
			<td align="center">{{res['run']['libc']}}</td>
			<% for t in ('dyninst','testsuite'):
					branch = res['run']['{0:s}_branch'.format(t)]
					commit = res['run']['{0:s}_commit'.format(t)]
					link = 'https://github.com/dyninst/{0:s}/commit/{1:s}'.format(t, commit)
					if branch[0:2] == 'PR':
						# pull request branches have the for PRXXX
						link = 'https://github.com/dyninst/{0:s}/pull/{1:s}'.format(t, branch[2:])
					end
			%>
				<td align="center">{{branch}}/<a href="{{link}}">{{commit[0:7]}}</a></td>
			% end
			<td align="center"><a href="{{ url('/logs') + '/' + res['run']['upload_file'] }}">Download</a></td>
		</tr>
		</table>
		<table style="margin-left:3%">
		<tr><td>
			<a href="{{ url('/regressions/run', curid=regs['base_commit']['id'], previd=res['run']['id']) }}">Direct link</a>
		</td></tr>
		</table>
		<br>
		% if res['regressions'] is not None:
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
				<th>Result</th>
				<th>Reason</th>
			</tr>
			% for r in res['regressions']:
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
			% end
			</table>
			<br><br>
		% else:
			<span style="margin-left:5%;font-size:150%;">No regressions found</span>
		% end
	% end
% end
</body>
</html>
