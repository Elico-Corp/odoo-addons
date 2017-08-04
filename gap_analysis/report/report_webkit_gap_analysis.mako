<html>
<head>
    <style type="text/css">
		body {font-family:helvetica;font-size:12px;line-height:14px;}
		.basic_table {text-align:center;border:1px solid lightGrey;border-collapse: collapse;}
		.basic_table td {border:1px solid lightGrey;font-size:12px;line-height:14px;padding:3px;vertical-align:middle;}
		.list_table {border-color:black;text-align:center;border-collapse: collapse;}
		.list_table td {border-color:gray;border-top:1px solid gray;text-align:left;font-size:12px;padding:3px;line-height:14px;}
		.list_table th {border-bottom:2px solid black;text-align:left;font-size:12px;font-weight:bold;padding:0 3px;line-height:14px;}
		.list_table thead { display:table-header-group;}
		table.gap_list_table tr th, table.gap_list_table tr td {vertical-align:middle;border-left:1px solid gray;}
		table.gap_list_table tr th.firsttd, table.gap_list_table tr td.firsttd {border-left:none;}
		#report_company_header {border:none;font-size:14px;line-height:16px;vertical-align:top;}
    </style>
</head>
<body>
	<table id="report_company_header" width="100%">
		<tr>
			<td width="50%">${helper.embed_logo_by_name('logo')|n}</td>
			<td>${company.partner_id.name |entity}<br />
			${company.partner_id.street |entity}<br />
			Phone: ${company.partner_id.phone |entity}<br />
			Mail: ${company.partner_id.email |entity}</td>
		</tr>
	</table>
	<br /><br />

    %for gap in objects :
    %if gap.partner_id:
    <% setLang(gap.partner_id.lang) %>
    %endif

    <table class="basic_table" width="100%">
        <tr><td>${_("Reference")}</td><td>${_("Document")}</td><td>${_("Date")}</td></tr>
        <tr><td>${gap.reference}</td><td>${gap.name}</td><td>${formatLang(gap.date_confirm, date=True)|entity}</td></tr>
    </table>
    <br /><br />
    
    <table class="list_table gap_list_table" width="100%">
        <%
        	types_id = []
        	types = gap._sorted_distinct_workloads(gap.id)
        	colspan = len(types)
        %>
        <thead>
        <tr>
        	<th class="firsttd" rowspan="2">&nbsp;</th>
        	<th rowspan="2">${_("Category")}</th>
        	<th rowspan="2">${_("Functionality")}</th>
        	<th rowspan="2" style="text-align:center;">${_("Effort")}</th>
        	<th colspan="${colspan}" style="text-align:center;border-bottom:1px solid gray;">${_("Duration (hours)")}</th>
        	<th rowspan="2" style="text-align:center;">${_("Estimate")}</th>
        </tr>
        <tr>
        	%for type in types:
        	<th style="text-align:center;">${type[1]}</th>
        	<% types_id.append(type[0]) %>
        	%endfor
        </tr>
        </thead>
        <tbody>
        %for line in gap.gap_lines :
        %if line.keep:
		<% effort = '' %>
		%if line.effort:
			<% effort = line.effort.name %>
		%endif
        <tr>
        	<td class="firsttd">${line.code|entity}</td>
        	<td>${line.category and line.category.full_path|entity}</td>
        	<td>${line.functionality.name}</td>
        	<td style="text-align:center;">${effort}</td>
        	%for type_id in types_id:
        	<td style="text-align:center;">${line._total_workloads(type_id) or 0}</td>
        	%endfor
        	<td style="text-align:right;">${formatLang(line.total_cost)}</td>
        </tr>
        %endif
        %endfor
        <% colspan = len(types_id) + 3 %>
        <tr>
        	<td class="firsttd" colspan="${colspan}" style="text-align:right;padding-right:5px;font-weight:bold;">${_("TOTAL:")}</td>
        	<td style="text-align:right;">${formatLang(gap.estimated_cost)}</td>
        </tr>
        </tbody>
    </table>        
    <p style="page-break-after:always"></p>
    %endfor
</body>
</html>