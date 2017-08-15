openerp.property_management = function (instance) {
	instance.web_calendar.QuickCreate.include({
        get_title: function () {
            var parent = this.getParent();
            if (_.isUndefined(parent)) {
                return _t("Create");
            }
            if (parent.name == 'tenancy.rent.schedule.calendar')
            	{
            	return _t("Create: ") + '<br/>' + 'Schedule Your Rent';
            	}
            else
            	{
	            var title = (_.isUndefined(parent.field_widget)) ?
	                    (parent.string || parent.name) :
	                    parent.field_widget.string || parent.field_widget.name || '';
	                    return _t("Create: ")  + title;
            	}
        },
    });
    var QWeb = openerp.web.qweb,
         _lt = openerp.web._lt;
         var _t = openerp.web._t;

    instance.web.client_actions.add('property.graph','instance.property_management.propertygraph');
    instance.property_management.propertygraph = instance.Widget.extend({
        template : 'propertygraph',

        start : function(){
            var self = this
            $("#type_of_graph").change(function(){
                self.setDynamicChart($(this)[0].value)
            });
            self.setDynamicChart('column')
        },

        setDynamicChart : function(chartype){
            var self = this;
            self.session.rpc("/web/graph_data").done(function(callback){
                $('#container_propertygraph').highcharts({
                    chart : {
                        height: 600,
                        type: chartype,
                    },
                    rangeSelector : {
                        inputEnabled: true,
                    },
                    title: {
                        text: _t('Property Graph'),
                        useHTML: Highcharts.hasBidiBug
                    },
                    xAxis: {
                        categories : callback[1],
                        title: {
                            text:_t('Proprty Name'),
                            useHTML: Highcharts.hasBidiBug
                        },
                    },
                    yAxis: {
                        title: {
                            text:_t('Prices'),
                            useHTML: Highcharts.hasBidiBug
                        },
                        labels: {
                            overflow: 'justify'
                        }
                    },
                    plotOptions: {
                        bar: {
                            dataLabels: {
                                enabled: true
                            }
                        },
                        pie: {
                            allowPointSelect: true,
                            cursor: 'pointer',
                            dataLabels: {
                                enabled: false
                            },
                            showInLegend: true
                        }
                    },
                    series:callback[0]
                });
            });
        },

    });
};
// vim:et fdc=0 fdl=0
