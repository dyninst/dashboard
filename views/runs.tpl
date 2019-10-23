<!DOCTYPE html>
<html>
<body>

% if len(runs) == 0:
		<span>No runs found</span>
% else:

	<table border="1">
	<%
		include('run.header.tpl')
		for r in runs:
			include('run.row.tpl', run=r, url=url)
		end
	%>
	</table>
% end

</body>
</html>
