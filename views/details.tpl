<!DOCTYPE html>
<html>
<body>

% if results is None:
	<span>No run found</span>
% else:

	<table border="1">
	<%
		include('run.header.tpl')
		include('run.row.tpl', run=results['run'], url=url)
	%>
	</table>
	<br>
	% for indices in [(0,1),(2,3)]:
	%	name=results['compilers'][indices[0]]['target'].title()
		<span style="font-size:25px;font-weight:bold">{{ name }} Compilers</span>
		<table border="1">
		<th>Name</th>
		<th>version</th>
		<th>language</th>
		<th>Path</th>
	%   for i in indices:
	%		c = results['compilers'][i] 
			<tr>
				<td align="left">{{ c['name'] }}</td>
				<td align="left">{{ c['version'] }}</td>
				<td align="center">{{ c['language'] }}</td>
				<td align="left">{{ c['path'] }}</td>
			</tr>
	%	end
		</table>
		<br>
	% end
% end

</body>
</html>
