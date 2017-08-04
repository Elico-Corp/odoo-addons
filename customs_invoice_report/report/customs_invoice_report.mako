<html>
<head>
    <style type="text/css">
        ${css}
        
        table{
        	border-left:1px solid  black;
        	border-right:1px solid  black;
        	border-top:1px solid  black;
        	border-bottom:1px solid  black;
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all; 
        }
        .table_no_border{
        	border-left:none;
        	border-right:none;
        	border-top:none;
        	border-bottom:none;
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
        }
        
        .table_horizontal_border{
        	frame:"vsides";
        	border-left:1px solid  black;
        	border-right:1px solid  black;
        	border-top:none;
        	border-bottom:none;
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
        	
        }
        .table_top_border{
        	border-left:1px solid  black;
        	border-right:1px solid  black;
        	border-top:1px solid  black;
        	border-bottom:'none';
        	
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
        }
        
		.underline {
			border:1px solid #002299;
			position:absolute;
			left:5px;
		}


		.left_td{border-left:0px solid  black;}  
		.top_td{border-top:0px solid  black;} 
		.right_td{border-right:0px solid  black;}  
		.bottom_td{border-bottom:0px solid  black;} 
		
		td{
        	border-left:1px solid  black;
        	border-right:1px solid  black;
        	border-top:1px solid  black;
        	border-bottom:1px solid  black;
         	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
		}
		th{
        	border-left:1px solid  black;
        	border-right:1px solid  black;
        	border-top:1px solid  black;
        	border-bottom:1px solid  black;
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
		}
		.tdh_no_border{
        	border-left:none;
        	border-right:none;
        	border-top:none;
        	border-bottom:none;
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
		}

		.td_all_border{
        	border-left:1px solid  black;
        	border-right:1px solid  black;
        	border-top:1px solid  black;
        	border-bottom:1px solid  black;
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
		}

		.new_page {page-break-after: always}
		.barcode39 {
		    font-family: "Free 3 of 9";
		    font-size: 36pt;
		}
    </style>
    
    
</head>
<body>
<% total_all = 0.0 %>

%for invoice in objects:
	<table class=table_no_border>
	    <tr class=table_no_border>
	    	<th class=table_no_border>
	    	   ${invoice.number or 'Draft Invoice'}
	    	</th>
	    </tr>
	 </table>
	 <table width='100%'>
	    <tr width='100%'>
	    	<th width='30%'>Description</th>
	    	<th width='20%'>Quantity</th>
	    	<th width='20%'>Unit Price</th>
	    	<th width='20%'>Price</th>
	    </tr>
	 </table>
	 	
     <table width='100%' class=table_no_border>
	    <tr width='100%'>
	        <td width='100%' class=table_no_border>
			    	%for line in invoice.invoice_line:
			    	    <table width='100%'>
			    	    <tr width='100%'>
			    	        <td width='30%'>${line.product_id.default_code} ${line.product_id.customs_description or ''}</td>
			    	        <td width='20%'>${line.quantity}  ${line.uos_id.name}</td>
			    	        <td width='20%'>${formatLang(line.price_unit * ratio,digits=get_digits(dp='Account'))}</td>
			    	        <td width='20%'>${invoice.currency_id.symbol} ${formatLang(line.price_subtotal * ratio,digits=get_digits(dp='Account'))} </td>
			    	    </tr>
			    	    </table>
			    	       
			    	%endfor
	             
	        </td>
	    </tr>
	 <table>
	 <table class=table_no_border>
	     <tr class=table_no_border>
	         <th class=table_no_border>Total:${invoice.currency_id.symbol} ${formatLang(invoice.amount_total * ratio,digits=get_digits(dp='Account'))}</th>
	         <% total_all += invoice.amount_total * ratio %>
	     </tr>
	 </table>
	 
	 <p></p>
%endfor


<p ><h1>Total ALL:${invoice.currency_id.symbol}  ${total_all} </h1></p>

</body>
</html>

<%doc>

	    	<th>
	    	Invoice: ${invoice.number or ''}
	    	<table class=table_no_border>
	    	%for line in invoice.invoice_line:
	    	    <tr>
	    	        <td>${line.product_id.default_code} ${line.product_id.customs_description or ''}</td>
	    	        <td>${line.quantity}</td>
	    	        <td>${line.price_unit * ratio}</td>
	    	    </tr>
	    	%endfor
	    	</table>
	    	</th>

Description
Taxes
 
 


</%doc>