openerp.web_url = function(instance) {

var QWeb = instance.web.qweb,
    _t = instance.web._t;

instance.web.ListView.List = instance.web.ListView.List.extend({
    render: function () {
        var self = this;
        this.$current.empty().append(
            QWeb.render('ListView.rows', _.extend({
                    render_cell: function () {
                        return self.render_cell.apply(self, arguments); }
                }, this)));
        this.records.each(function(record){
            var $row = self.$current.find('[data-id=' + record.get('id') + ']');
            for(var i=0, length=self.columns.length; i<length; ++i) {
            //alert(self.columns[i].name);
		if(self.columns[i].widget === 'url') {
                	var $cell = $row.find((_.str.sprintf('[data-field=%s]', self.columns[i].id)));
                	$cell.html(_.template('<a class="oe_form_uri" href="<%-text%>" target="blank" data-model="<%-model%>" data-id="<%-id%>"><%-text%></a>', 	{
                        text: instance.web.format_value(record.get(self.columns[i].id), self.columns[i], ''),
                        model: self.columns[i].relation,
                        id: record.get(self.columns[i].id)[0]
                    	}))
                }
            }
        });
        this.pad_table_to(4);
    }
});

 
instance.web.form.One2ManyList = instance.web.form.One2ManyList.extend({
	render: function () {
        var self = this;
        this.$current.empty().append(
            QWeb.render('ListView.rows', _.extend({
                    render_cell: function () {
                        return self.render_cell.apply(self, arguments); }
                }, this)));
        this.records.each(function(record){
            var $row = self.$current.find('[data-id=' + record.get('id') + ']');
            for(var i=0, length=self.columns.length; i<length; ++i) {
                if(self.columns[i].widget === 'url') {
                	var $cell = $row.find((_.str.sprintf('[data-field=%s]', self.columns[i].id)));
                	$cell.html(_.template('<a class="oe_form_uri" href="<%-text%>" target="blank" data-model="<%-model%>" data-id="<%-id%>"><%-text%></a>', {
                        text: instance.web.format_value(record.get(self.columns[i].id), self.columns[i], ''),
                        model: self.columns[i].relation,
                        id: record.get(self.columns[i].id)[0]
                    	}))
                }
            }
        });
        this.pad_table_to(4);
    }
  }); 
};
