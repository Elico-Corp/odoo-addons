function openerp_picking_widgets_extend(instance){
    var module = instance.stock;
    var _t = instance.web._t;
    var QWeb   = instance.web.qweb;
    var PackOperationCache=new Object(); // 缓存operations的对象
    PackOperationCache.operations =[];
    PackOperationCache.cur_operation_id = false;

    module.PickingMainWidget.include({
        start: function() {
            this._super();
            //数据加载完后绑定keypress事件
            this.barcode_scanner.connect(function(ean){
            });
        },
        //重写方法
        load: function(picking_id){
            var self = this;
            function load_picking_list(type_id){
                var pickings = new $.Deferred();
                new instance.web.Model('stock.picking')
                    .call('get_next_picking_for_ui',[{'default_picking_type_id':parseInt(type_id)}])
                    .then(function(picking_ids){
                        if(!picking_ids || picking_ids.length === 0){
                            (new instance.web.Dialog(self,{
                                title: _t('No Picking Available'),
                                buttons: [{
                                    text:_t('Ok'),
                                    click: function(){
                                        self.menu();
                                    }
                                }]
                            }, _t('<p>We could not find a picking to display.</p>'))).open();

                            pickings.reject();
                        }else{
                            self.pickings = picking_ids;
                            pickings.resolve(picking_ids);
                        }
                    });

                return pickings;
            }

            // if we have a specified picking id, we load that one, and we load the picking of the same type as the active list
            if( picking_id ){
                var loaded_picking = new instance.web.Model('stock.picking')
                    .call('read',[[parseInt(picking_id)], ['picking_type_id'], new instance.web.CompoundContext()])
                    .then(function(picking){
                        self.picking = picking[0];
                        self.picking_type_id = picking[0].picking_type_id[0];
                        return load_picking_list(self.picking.picking_type_id[0]);
                    });
            }else{
                // if we don't have a specified picking id, we load the pickings belong to the specified type, and then we take
                // the first one of that list as the active picking
                var loaded_picking = new $.Deferred();
                load_picking_list(self.picking_type_id)
                    .then(function(){
                        return new instance.web.Model('stock.picking').call('read',[self.pickings[0],['picking_type_id'], new instance.web.CompoundContext()]);
                    })
                    .then(function(picking){
                        self.picking = picking;
                        self.picking_type_id = picking.picking_type_id[0];
                        loaded_picking.resolve();
                    });
            }

            return loaded_picking.then(function(){
                    return new instance.web.Model('stock.location').call('search',[[['usage','=','internal']]]).then(function(locations_ids){
                        return new instance.web.Model('stock.location').call('read',[locations_ids, ['id','name']]).then(function(locations){
                            self.locations = locations;
                        });
                    });
                }).then(function(){
                    return new instance.web.Model('stock.picking').call('check_group_pack').then(function(result){
                        return self.show_pack = result;
                    });
                }).then(function(){
                    return new instance.web.Model('stock.picking').call('check_group_lot').then(function(result){
                        return self.show_lot = result;
                    });
                }).then(function(){
                    if (self.picking.pack_operation_exist === false){
                        self.picking.recompute_pack_op = false;
                        return new instance.web.Model('stock.picking').call('do_prepare_partial',[[self.picking.id]]);
                    }
                }).then(function(){
                        if (PackOperationCache.cur_operation_id !== false){
                            return [PackOperationCache.cur_operation_id]
                        }
                        return new instance.web.Model('stock.pack.operation').call('search',[[['picking_id','=',self.picking.id]]])
                }).then(function(pack_op_ids){
                        return new instance.web.Model('stock.pack.operation').call('read',[pack_op_ids, ['id','name','qty_done','product_qty', 'processed','result_package_id','product_id','package_id','product_uom_id','lot_id','location_id','location_dest_id'], new instance.web.CompoundContext()])
                }).then(function(operations){
                    // 为了提高扫描的响应数度, 第一次加载数据时缓存Operations,每次扫描时不再读取全部Operation,只读取扫描的那一条, 将读取operation的时间从2秒降低到20毫秒
                    var package_ids = [];
                    var operations_cache = PackOperationCache.operations;

                    for(var i = 0; i < operations.length; i++){
                        if(!_.contains(package_ids,operations[i].result_package_id[0])){
                            if (operations[i].result_package_id[0]){
                                package_ids.push(operations[i].result_package_id[0]);
                            }
                        }

                        var updated = false
                        for(var j = 0; j < operations_cache.length; j++){
                            if (operations_cache[j].id == operations[i].id){
                                operations_cache[j] = operations[i]; // 更新当前扫描的数据到缓存
                                updated = true;
                                break;
                            }
                        }
                        if (updated == false){
                            operations_cache.push(operations[i]) // 新创建的行, 添加到缓存
                        }

                        if (PackOperationCache.cur_operation_id !=false){// 在原来的行上减数
                            for(var j = 0; j < operations_cache.length; j++){
                                if (operations_cache[j].product_id[0] == operations[i].product_id[0] && operations_cache[j].lot_id == false && operations_cache[j].product_qty > 0){
                                    operations_cache[j].product_qty -=1;
                                    if (operations_cache[j].product_qty<=0){
                                        operations_cache.splice(j,1) //删除扫描完的行
                                    }
                                    break;
                                }
                            }
                        }
                    }
                    PackOperationCache.operations = operations_cache
                    PackOperationCache.cur_operation_id = false;
                    $("header").data(PackOperationCache);
                    // 把缓存数据赋值给 self.packoplines, 后面的代码会把这些数据刷新到前台。 
                    self.packoplines = PackOperationCache.operations

                    return new instance.web.Model('stock.quant.package').call('read',[package_ids, [], new instance.web.CompoundContext()])
                }).then(function(packages){
                    self.packages = packages;
                }).then(function(){
                        return new instance.web.Model('product.ul').call('search',[[]])
                }).then(function(uls_ids){
                        return new instance.web.Model('product.ul').call('read',[uls_ids, []])
                }).then(function(uls){
                    self.uls = uls;
                });
        },
        // 重写方法, 扫描时记录当前扫描的operation id
        scan: function(ean){ //scans a barcode, sends it to the server, then reload the ui
            var self = this;
            var product_visible_ids = this.picking_editor.get_visible_ids();
            return new instance.web.Model('stock.picking')
                .call('process_barcode_from_ui', [self.picking.id, ean, product_visible_ids])
                .then(function(result){
                    if (result.filter_loc !== false){
                        //check if we have receive a location as answer
                        if (result.filter_loc !== undefined){
                            var modal_loc_hidden = self.$('#js_LocationChooseModal').attr('aria-hidden');
                            if (modal_loc_hidden === "false"){
                                var line = self.$('#js_LocationChooseModal .js_loc_option[data-loc-id='+result.filter_loc_id+']').attr('selected','selected');
                            }
                            else{
                                self.$('.oe_searchbox').val(result.filter_loc);
                                self.on_searchbox(result.filter_loc);
                            }
                        }
                    }
                    if (result.operation_id !== false){
                        PackOperationCache.cur_operation_id = result.operation_id; //记录当前扫描的operation id
                        self.refresh_ui(self.picking.id).then(function(){
                            return self.picking_editor.blink(result.operation_id);
                        });
                    }
                });
        },
    });


    module.BarcodeScanner.include({
        //重写方法
        connect: function(callback){
            var code = "";
            var timeStamp = 0;
            var timeout = null;

            this.handler = function(e){
                if(e.which === 13){ //ignore returns
                    return;
                }

                if(timeStamp + 50 < new Date().valueOf()){
                    code = "";
                }

                timeStamp = new Date().valueOf();
                clearTimeout(timeout);

                code += String.fromCharCode(e.which);
                timeout = setTimeout(function(){
                    if(code.length >= 3){
                        callback(code);
                    }
                    code = "";
                },150);//100时只能读到12个字符，导致读到的13个字符的条码不完整。故由100改成150

            };

            $('body').on('keypress', this.handler);

        },
    });
}

openerp.stock_extend = function(openerp) {
    openerp.stock_extend = openerp.stock_extend || {};
    openerp_picking_widgets_extend(openerp);
}