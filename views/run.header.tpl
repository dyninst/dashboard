<%
# The header for displaying a run or sequence of runs
%>

<style style="text/css">
	tr:hover {
		background-color: #F0F0F0
	}
</style>


<table border="1" id="results">
<tr>
<th onclick="w3.sortHTML('#results', '.item', 'td:nth-child(1)')" style="cursor:pointer">Run</th>
<th onclick="w3.sortHTML('#results', '.item', 'td:nth-child(2)')" style="cursor:pointer">Date</th>
<th onclick="w3.sortHTML('#results', '.item', 'td:nth-child(3)')" style="cursor:pointer">Arch</th>
<th onclick="w3.sortHTML('#results', '.item', 'td:nth-child(4)')" style="cursor:pointer">Host</th>
<th onclick="w3.sortHTML('#results', '.item', 'td:nth-child(5)')" style="cursor:pointer">Compiler Name</th>
<th onclick="w3.sortHTML('#results', '.item', 'td:nth-child(6)')" style="cursor:pointer">libc</th>
<th onclick="w3.sortHTML('#results', '.item', 'td:nth-child(7)')" style="cursor:pointer">Dyninst Build</th>
<th onclick="w3.sortHTML('#results', '.item', 'td:nth-child(8)')" style="cursor:pointer">Tests Build</th>
<th>Test Results</th>
<th onclick="w3.sortHTML('#results', '.item', 'td:nth-child(9)')" style="cursor:pointer">Regressions</th>
<th onclick="w3.sortHTML('#results', '.item', 'td:nth-child(10)')" style="cursor:pointer">Dyninst</th>
<th onclick="w3.sortHTML('#results', '.item', 'td:nth-child(11)')" style="cursor:pointer">Testsuite</th>
<th>Log Files</th>
</tr>
