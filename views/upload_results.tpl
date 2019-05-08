<!DOCTYPE html>
<html>
<body>

<p style="font-size:30px">Results:</p>
<table border="1">

<tr>
<th>Arch</th>
<th>Host</th>
<th>libc</th>
<th>Build Status</th>
<th>Dyninst</th>
<th>Testsuite</th>
<th>Log File</th>
</tr>

<tr>
<td align="center">{{results['arch']}}</td>
<td align="center">{{results['hostname']}}</td>
<td align="center">{{results['libc']}}</td>
<%
if results['build_status'] == 'OK':
	bgcolor='#58FA58'
else:
	bgcolor='#FA5858'
end
%>
<td align="center" bgcolor={{bgcolor}}>{{results['build_status']}}</td>

<td align="center">{{results['dyninst_branch'] + ' / ' + results['dyninst_commit'][0:7]}}</td>
<td align="center">{{results['testsuite_branch'] + ' / ' + results['testsuite_commit'][0:7]}}</td>
<td align="center"><a href="{{results['user_file']}}" download>Download</a></td>
</tr>

</table>

</body>
</html>
