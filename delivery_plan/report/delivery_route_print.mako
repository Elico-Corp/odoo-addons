<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
    <head>
        <meta content="text/html; charset=UTF-8" http-equiv="content-type"> 
        <style type="text/css">
        	${css}
        </style>
    </head>
    <body>
    <% cpt = 0 %>
        %for delivery_route in objects :
%if cpt > 0:
<div style="page-break-after: always;"><span style="display: none;"> </span></div>
%endif
		<div class="title">Delivery Distribution Control Sheet (配送交接控制表)</div>
		<div style="font-size:12px;font-style:italic;text-align:center;">Ref / 编号 : ${delivery_route.name}</div>
		<td><b></b></td><td></td>
		<br />
		<table class="basic_table" width="100%">
		<tr>
		    <td width="17%"><b>Date<br />日期</b></td><td width="33%">${delivery_route.date}</td>
		    <td width="17%"><b>Time Slot<br />时间段</b></td><td>${delivery_route.dts_id.name or '&nbsp;'}</td>
		</tr>
		<tr>
			<td><b>Driver<br />驾驶员</b></td><td>${delivery_route.driver_id.name or '&nbsp;'}</td>
		    <td><b>Deliver<br />送货员</b></td><td>${delivery_route.picker_id.name or '&nbsp;'}</td>
		</tr>
		<tr>
			<td><b>Departure Time<br />出发时间</b></td><td>${delivery_route.departure_date or '&nbsp;'}</td>
		    <td><b>Operation Rep<br />运营人员</b></td><td></td>
		</tr>
		</table>
		<br />
        <div class="main">
            <table width="100%" class="basic_table">
                <tbody>
                    <tr style="font-weight:bold;">
                    	<td style="height:26px;" colspan="4">Reason for delayed/Early departure 延迟的原因</td>
                    	<td colspan="2">出库公里数: </td>
                    	<td colspan="2">回库公里数: </td>
                    </tr>
                    <tr style="font-weight:bold;">
                    	<td style="vertical-align:top; height:30px;" colspan="8">&nbsp;</td>
                    </tr>
                    <tr style="font-weight:bold;">
                    	<td style="text-align:center; height:16px;" colspan="8">List of deliveries / 交货清单</td>
                    </tr>
                    <tr style="font-weight:bold;">
                    	<td style="vertical-align:top; width:15px;">No</td>
                    	<td style="vertical-align:top; width:70px;">Order <br /> 单号</td>
                    	<td style="vertical-align:top; width:48px;">T<br />装箱</td>
                        <td style="vertical-align:top; width:175px;">Address<br />地址</td>
                        <td style="vertical-align:top;">Time<br />时间要求</td>
                        <td style="vertical-align:top;">Payment<br />支付方式</td>
                        <td style="vertical-align:top; width:75px;">Arrive Time<br />到达时间</td>
                        <td style="vertical-align:top; width:75px;">Observation<br />结果</td>
                    </tr>
                    <% cpt=0 %>
                    %for line in delivery_route.line_ids:
                    	<% cpt+=1 %>
                    	<% iced  = False %>
            			<% warm  = False %>
            			<% other = False %>
                    %if line.vip:
                    <tr style="font-style:italic;">
                    %else:
                    <tr>
					%endif
                    	<td style="vertical-align: top;"><div class="dontcutme">${cpt}</div></td>
                    	<td style="vertical-align: top;"><div class="dontcutme">${line.origin and line.origin or ''}<!--${line.picking_id.name and '('+ line.picking_id.name + ')' or ''}--></div></td>
                    	<td style="vertical-align: top;"><div class="dontcutme"><%
                        pack_set = set([ move.product_id.joomla_deliver_in for move in line.picking_id.move_lines ])
                        %>
                        % for pack in pack_set:
                        	%if pack in ['warm', 'iced', 'iced_n_warm','cold']:
                    			%if pack in ['iced', 'iced_n_warm'] and not iced:
	                    			<input type="checkbox" /> 冻F<br />
	                    			<% iced = True %>
	                			%endif
	                			%if pack in ['warm', 'iced_n_warm'] and not warm:
	                    			<input type="checkbox" /> 热W<br />
	                    			<% warm = True %>
	                    		%endif
	                    		%if pack in ['cold']:
	                    			<input type="checkbox" /> 冷C<br />
	                    			<% warm = True %>
	                    		%endif
                			%else:
                				%if not other:
                    				<input type="checkbox" /> 常温<br />
                    				<% other = True %>
                    			%endif
                    		%endif
                    	%endfor
                        </div></td>
                        <td style="vertical-align: top;"><div class="dontcutme">${line.address_id.name or  ''}<br />${line.street or line.address_id.street or  ''}</div></td>
		                <td style="vertical-align: top;"><div class="dontcutme">${line.customer_date or ''}</div></td>
		                <td style="vertical-align: top;"><div class="dontcutme">${line.so_payment_method or ''}</div></td>
                        <td style="vertical-align: top;">&nbsp;</td>
                        <td style="vertical-align: top;">&nbsp;</td>
                    </tr>
                    %endfor
                </tbody>
            </table>
        </div>
        <div style="page-break-after: auto;"><span style="display: none;"> </span></div>
        <% cpt+=1 %>
        %endfor
    </body>
</html>