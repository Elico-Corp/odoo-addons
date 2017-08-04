<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
    <head>
  <meta content="text/html; charset=UTF-8" http-equiv="content-type"> 
  <style type="text/css">
    ${css}
    table
    {
        border-collapse:collapse;
    }
    .none_break,tr {
        page-break-inside: avoid;
    }

    td
    {
        border: 1px solid black;
        border-collapse:collapse;
        font-size:12px;
    }
  </style>
  <title></title>
  </head>
  <body>
  <table style="text-align: left; width: 100%;border-style: none;"  cellpadding="2" cellspacing="2">
<% 
setLang(loginuser.lang)
%>
<p style="text-align:center;font-weight: bold;font-size:16px" >${_("Stock Slow Moving")}</p> 
  <tbody>
    <tr>
      <td style="vertical-align: top; width:7%">${_('Product Code')}</td>
      <td style="vertical-align: top; width:10%">${_('Product Name')}</td>
      <td style="vertical-align: top; text-align:right;width:8%">${_('Onhand Quantity')}</td>
      <td style="vertical-align: top; width:7%">${_('Last Sale Date')}</td>
      <td style="vertical-align: top; text-align:right;width:8%">${_('Last Sale Quantity')} </td>
      <td style="vertical-align: top; width:7%">${_('Last Purchase Date')}</td>
      <td style="vertical-align: top; text-align:right;width:8%">${_('Last Purchase Quantity')} </td>
      <td style="vertical-align: top; width:7%">${_('Last Production Date')}</td>
      <td style="vertical-align: top; text-align:right;width:8%">${_('Last Production Quantity')} </td>
      <td style="vertical-align: top; text-align:right;width:8%">${_('Last 6-Month Quantity')} </td>
      <td style="vertical-align: top; text-align:right;width:8%">${_('Last Year Quantity')} </td>
      <td style="vertical-align: top; text-align:right;width:7%">${_('Sale Rotation')} </td>
      <td style="vertical-align: top; width:7%">${_('Creation Date')}</td>
    </tr>
%for line in objects:
    <tr>
      <td style="vertical-align: top;">${line.product_id.default_code or ''}</td>
      <td style="vertical-align: top;">${line.product_id.name or ''}</td>
      <td style="vertical-align: top; text-align:right;">${formatLang(line.onhand_qty,digits=2)}</td>

      <td style="vertical-align: top;">${formatLang(line.lasts_date,date=True)}</td>
      <td style="vertical-align: top; text-align:right;">${line.lasts_date and formatLang(line.lasts_qty,digits=2) or ''}</td>

      <td style="vertical-align: top;">${formatLang(line.lastp_date,date=True)}</td>
      <td style="vertical-align: top; text-align:right;">${line.lastp_date and formatLang(line.lastp_qty,digits=2) or ''}</td>

      <td style="vertical-align: top;">${formatLang(line.lastm_date,date=True)}</td>
      <td style="vertical-align: top; text-align:right;">${line.lastm_date and formatLang(line.lastm_qty,digits=2) or ''}</td>

      <td style="vertical-align: top; text-align:right;">${formatLang(line.product_lastq_qty,digits=2)}</td>
      <td style="vertical-align: top; text-align:right;">${formatLang(line.product_lasty_qty,digits=2)}</td>
      <td style="vertical-align: top; text-align:right;">${formatLang(line.rotation_rate,digits=2)}</td>
      <td style="vertical-align: top;">${formatLang(line.date,date=True)}</td>
    </tr>
%endfor
</tbody>
</table>
</body>
</html>
