<html>
<head>
    <style type="text/css">
        ${css}
        .note{
               margin-top: 10px;
               margin-bottom: 10px;
               font-size:12px;
               text-align:left;
              }
    </style>
</head>
<body>
    %for o in objects :
    <% setLang(o.partner_id.lang) %>
       <table class="header" style="border-bottom: 0px solid black; width: 100%">
            <tr>
                <td>${helper.embed_image('jpeg',str(o.company_id.logo),150)}</td>
            </tr>
        </table>
     <table class="dest_address" width="100%">
        <tr>
            <td width="30%">
                <b>${o.partner_id and o.partner_id.title and o.partner_id.title.name or ''|entity} ${o.partner_id and o.partner_id.name or '' |entity}</b></br>
                ${o.partner_id.street or ''|entity}</br>
                %if o.partner_id.street2 :
                    ${o.partner_id.street2 or ''|entity}</br>
                %endif
                ${o.partner_id.zip or ''|entity} ${o.partner_id.city or ''|entity}</br>
                %if o.partner_id.country_id :
                    ${o.partner_id.country_id.name or ''|entity}</br>
                %endif
                %if o.partner_id.phone :
                    ${_("Tel")}: ${o.partner_id.phone|entity}</br>
                %endif
                %if o.partner_id.fax :
                    ${_("Fax")}: ${o.partner_id.fax|entity}</br>
                %endif
                %if o.partner_id.email :
                    ${_("E-mail")}: ${o.partner_id.email|entity}</br>
                %endif
                %if o.partner_id.vat :
                    ${_("VAT")}: ${o.partner_id.vat|entity}</br>
                %endif
            </td>
            <td width="50%">
            </td>
            <td width="20%">
                <b>${o.company_id and o.company_id.name or '' |entity}</b></br>
                ${o.company_id.street or ''|entity}</br>
                %if o.company_id.street2 :
                    ${o.company_id.street2 or ''|entity}</br>
                %endif
                ${o.company_id.zip or ''|entity} ${o.company_id.city or ''|entity}</br>
                %if o.company_id.country_id :
                    ${o.company_id.country_id.name or ''|entity}</br>
                %endif
                %if o.company_id.phone :
                    ${_("Tel")}: ${o.company_id.phone|entity}</br>
                %endif
                %if o.company_id.fax :
                    ${_("Fax")}: ${o.company_id.fax|entity}</br>
                %endif
                %if o.company_id.email :
                    ${_("E-mail")}: ${o.company_id.email|entity}</br>
                %endif
                %if o.company_id.vat :
                    ${_("VAT")}: ${o.company_id.vat|entity}</br>
                %endif
            </td>
       </tr>   
       </table>
       <table class="dest_address" width="100%">
       <tr>
       <td width="20%">
    		<span class="title">${_("Invoice")}       ${o.name  or ''|entity}</span>
       </td>
		<td width="60%">
			
		</td>
    	%if o.company_id:
       	<td width="20%">
			${o.company_id.country_id.name or ''|entity},   ${formatLang(o.date_order,date = True) |entity}
       	</td>
    	%endif
       </tr>  
    </table>
    <br/>
    <br/>
    
    <b>Dear ${o.partner_id.name or '' |entity},</b></br>
            ${_("Thank you for your order! Please find the details bellow.")}</br>
            ${_("kindly arrange payment to our account number")}
            %for bank in o.company_id.bank_ids:
             ${bank.acc_number or ''|entity}
             at ${bank.bank_name or '' |entity},</br>
              ${_("SWIFT/IBNA:")} ${bank.swift_ibna or '' |entity}
            %endfor
		<% 
			subtotal=0.0
			list =[]
		%>	
		<table class="basic_table" width="100%">
		%for rec in curr_group(o.order_line):
				%if not curr_rec(rec[0]):
					<tr><td><b>${_("POS")}</b></td>
						<td><b>${_("Product Name")}</b></td>
						<td width="20%"><b>${_("Spec")}</b></td><td>
						<b>${_("Qty")}</b></td><td>
						<b>${_("Price")}(${o.currency_id.name})</b></td>
						<td><b>${_("Total")}(${o.currency_id.name})</b></td>
					</tr>
				%else:
					<tr>
						<td><b>${_("POS")}</b></td>
						<td><b>${_("Product Name")}</b></td>
						<td><b>${_("Spec")}</b></td>
						<td><b>${_("Qty")}</b></td>
						<td><b>${_("Price")}(${curr_rec(rec[0])})</b></td>
						<td><b>${_("Total")}(${curr_rec(rec[0])})</b></td>
					</tr>
				%endif
				<%
					total = 0.0
					dis = 0.0
					com_total = 0.0
				%>
				%for line in curr_line(o.order_line):
					%if rec[0] == line[2] and rec[1] == line[6]:
						<%
							
							total = total +(line[4] * line[3])
							if line[5]:
								dis =dis + ((compute_currency(o.currency_id.id,rec[0],line[4] * line[3]) * line[5])/100)
						%>
						<tr>
							<td>${line[0] or ' ' |entity}</td>
							<td>${line[1] or ''|entity}</td><td>${line[2] or ''|entity}</td>
							<td>${formatLang(line[3]) or '' |entity}</td>
							<td>${formatLang(compute_currency(o.currency_id.id,rec[0],line[4]), dp='Account')}</td>
							<td>${formatLang(compute_currency(o.currency_id.id,rec[0],line[4] * line[3]), dp='Account')}</td>
						</tr>
					%endif
				%endfor
				<% subtotal= subtotal+(total) %>
				%if not curr_rec(rec[0]):
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Sub-total")}(${o.currency_id.name})</b></td>
						<td style="text-align:right"><b>${formatLang(total, dp='Account')}</b></td>
					</tr>
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Discount")}</b></td>
						<td style="text-align:right"><b>${formatLang(dis, dp='Account')}</b></td>
						
					</tr>
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right">
						<b>${_("Sub-total")}(${o.currency_id.name})</b></td>
						<td style="text-align:right"><b>${formatLang((total-dis), dp='Account')}</b></td>
					</tr>
##					<tr>
##						<td style="border-style:none"/>
##						<td style="border-style:none"/>
##						<td style="border-style:none"/>
##						<td style="border-style:none"/>
##						<td style="text-align:right"><b>${_("Sub-total")}(${o.company_id.currency_id.name})</b></td>
##						
##						%if o.currency_id.id != o.company_id.currency_id.id:
##							<td style="text-align:right"><b>${formatLang(compute_currency(o.currency_id.id,o.company_id.currency_id.id,total)-dis, dp='Account')}</b></td>
##						%else:
##							<td style="text-align:right"><b>${formatLang((total-dis), dp='Account')}</b></td>
##						%endif
##					</tr>
				%elif curr_rec(rec[0]) == o.currency_id.name and curr_rec(rec[0]) == o.company_id.currency_id.name :
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Sub-total")}(${curr_rec(rec[0])})</b></td>
						<td style="text-align:right"><b>${formatLang(total, dp='Account')}</b></td>
					</tr>
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Discount")}</b></td>
						<td style="text-align:right"><b>${formatLang(dis, dp='Account')}</b></td>
					</tr>
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Sub-total")}(${curr_rec(rec[0])})</b></td>
						<td style="text-align:right"><b>${formatLang((total-dis), dp='Account')}</b></td>
					</tr>
				%elif curr_rec(rec[0]) == o.currency_id.name and curr_rec(rec[0]) != o.company_id.currency_id.name:
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Sub-total")}(${curr_rec(rec[0])})</b></td>
						<td style="text-align:right"><b>${formatLang(total, dp='Account')}</b></td>
					</tr>
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Discount")}</b></td>
						<td style="text-align:right"><b>${formatLang(dis, dp='Account')}</b></td>
					</tr>
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Sub-total")}(${curr_rec(rec[0])})</b></td>
						<td style="text-align:right"><b>${formatLang((total-dis), dp='Account')}</b></td>
					</tr>
##					<tr>
##						<td style="border-style:none"/>
##						<td style="border-style:none"/>
##						<td style="border-style:none"/>
##						<td style="border-style:none"/>
##						<td style="text-align:right"><b>${_("Sub-total")}(${o.company_id.currency_id.name})</b></td>
##						<td style="text-align:right"><b>${formatLang(compute_currency(o.currency_id.id,o.company_id.currency_id.id,total), dp='Account')}</b></td>
##					</tr>
				%elif curr_rec(rec[0]) != o.currency_id.name and curr_rec(rec[0]) ==  o.company_id.currency_id.name:
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Sub-total")}(${curr_rec(rec[0])})</b></td>
						<td style="text-align:right"><b>${formatLang(compute_currency(o.currency_id.id,rec[0],total), dp='Account')}</b></td>
					</tr>
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Discount")}</b></td>
						<td style="text-align:right"><b>${formatLang(dis, dp='Account')}</b></td>
					</tr>
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Sub-total")}(${curr_rec(rec[0])})</b></td>
						<td style="text-align:right"><b>${formatLang((compute_currency(o.currency_id.id,rec[0],total)-dis), dp='Account')}</b></td>
					</tr>
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Sub-total")}(${o.currency_id.name})</b></td>
						<td style="text-align:right"><b>${formatLang(compute_currency(rec[0],o.currency_id.id,(compute_currency(o.currency_id.id,rec[0],total)-dis)), dp='Account')}</b></td>
					</tr>
				%elif o.currency_id.name == o.company_id.currency_id.name and o.currency_id.name != curr_rec(rec[0]):
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Sub-total")}(${curr_rec(rec[0])})</b></td>
						<td style="text-align:right"><b>${formatLang(compute_currency(o.currency_id.id,rec[0],total), dp='Account')}</b></td>
					</tr>
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Discount")}</b></td>
						<td style="text-align:right"><b>${formatLang(dis, dp='Account')}</b></td>
					</tr>
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Sub-total")}(${curr_rec(rec[0])})</b></td>
						<td style="text-align:right"><b>${formatLang((compute_currency(o.currency_id.id,rec[0],total)-dis), dp='Account')}</b></td>
						
					</tr>
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Sub-total")}(${o.currency_id.name})</b></td>
						<td style="text-align:right"><b>${formatLang(total, dp='Account')}</b></td>
					</tr>
				%else:
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Sub-total")}(${curr_rec(rec[0])})</b></td>
						<td style="text-align:right"><b>${formatLang(compute_currency(o.currency_id.id,rec[0],total), dp='Account')}</b></td>
					</tr>
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Discount")}</b></td>
						<td style="text-align:right"><b>${formatLang(dis, dp='Account')}</b></td>
					</tr>
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Sub-total")}(${curr_rec(rec[0])})</b></td>
						<td style="text-align:right"><b>${formatLang((compute_currency(o.currency_id.id,rec[0],total)-dis), dp='Account')}</b></td>
						<%com_total = float(formatLang((compute_currency(o.currency_id.id,rec[0],total)-dis), dp='Account')) %>
					</tr>
##					<tr>
##						<td style="border-style:none"/>
##						<td style="border-style:none"/>
##						<td style="border-style:none"/>
##						<td style="border-style:none"/>
##						<td style="text-align:right"><b>${_("Sub-total")}(${o.company_id.currency_id.name})</b></td>
##						<td style="text-align:right"><b>${formatLang(compute_currency(rec[0],o.company_id.currency_id.id,compute_currency(o.currency_id.id,rec[0],total)), dp='Account')}</b></td>
##					</tr>
					<tr>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="border-style:none"/>
						<td style="text-align:right"><b>${_("Sub-total")}(${o.currency_id.name})</b></td>
						<td style="text-align:right"><b>${formatLang(compute_currency(rec[0],o.currency_id.id,com_total), dp='Account')}</b></td>
					</tr>
				%endif
		%endfor
				<tr>
					<td style="border-style:none"/>
					<td style="border-style:none"/>
					<td style="border-style:none"/>
					<td style="border-style:none"/>
					<td style="text-align:right"><b>${_("Total")}(${o.currency_id.name})</b></td>
					<td style="text-align:right"><b>${formatLang(o.amount_total)}</b></td>
				</tr>
	</table>
	<p style="page-break-after:always"></p>
 %endfor
</body>
</html>
