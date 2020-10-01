var price; //电影票价
$(document).ready(function () {
    var $cart = $('#seats_chose'), //座位区
        $tickects_num = $('#tickects_num'), //票数
        $total_price = $('#total_price'); //票价总额

    var sc = $('#seat_area').seatCharts({
        map: [//座位结构图 a 代表座位; 下划线 "_" 代表过道
            'cccccccccc',
            'cccccccccc',
            '__________',
            'cccccccc__',
            'cccccccccc',
            'cccccccccc',
            'cccccccccc',
            'cccccccccc',
            'cccccccc__',
            'cccccccc__'
        ],
        naming: {//设置行列等信息
            top: false, //不显示顶部横坐标（行）
            getLabel: function (character, row, column) { //返回座位信息
                return column;
            }
        },
        legend: {//定义图例
            node: $('#legend'),
            items: [
                ['c', 'available', '可选座'],
                ['c', 'unavailable', '已售出']
            ]
        },
        click: function () {
            if (this.status() == 'available') { //若为可选座状态，添加座位
                $('<li>' + (this.settings.row + 1) + '排' + this.settings.label + '座</li>')
                    .attr('id', 'cart-item-' + this.settings.id)
                    .data('seatId', this.settings.id)
                    .appendTo($cart);

                $tickects_num.text(sc.find('selected').length + 1); //统计选票数量
                $total_price.text(getTotalPrice(sc) + price);//计算票价总金额

                return 'selected';
            } else if (this.status() == 'selected') { //若为选中状态

                $tickects_num.text(sc.find('selected').length - 1);//更新票数量
                $total_price.text(getTotalPrice(sc) - price);//更新票价总金额
                $('#cart-item-' + this.settings.id).remove();//删除已预订座位

                return 'available';
            } else if (this.status() == 'unavailable') { //若为已售出状态
                return 'unavailable';
            } else {
                return this.style();
            }
        }
    });
     //获取票价
    var ur = location.href;//获取地址
    var Cfilm_id = ur.split('?')[1].split('=')[1];
    document.getElementById("Cfilm_ID").value = Cfilm_id
    post_data = {"Cfilm_id": Cfilm_id};
    $.ajax({
        url: "/myapp/getprice/",
        type: 'POST',
        data: post_data,
        async: false,
        success: function (price_) {
            price = parseInt(price_); //电影票价
        },
        error: function () {
            // alert("服务器请求超时,请重试!");
        }
    })

    $.ajax({
        url: "/myapp/getseat/",
        type: 'POST',
        data: post_data,
        success: function (local) {
            if (local){
            local_seat = JSON.parse(local).seat_list;
            sc.get(local_seat).status('unavailable');
            }
            else{
                console.log("ok!")

            }
        },
        error: function () {
            alert("服务器请求超时,请重试!");
        }
    })
});

function getTotalPrice(sc) { //计算票价总额
    var total = 0;
    sc.find('selected').each(function () {
        total += price;
    });
    return total;
}

//支付
function pay() {
    var total = document.getElementById("total_price").innerHTML;  //total 支付价格
    document.getElementById("input1").value = total;
    a = document.getElementById("input1").value;
    var seats = document.getElementById("seats_chose").childNodes;
    var sql_local = "";
    var tep = "#"

    jQuery(seats).each(  //循环获取li的id值
        function () {
            var ids = $(this).attr("id");
            var seat_value = ids.split('-')[2];  //获取座位id
            sql_local = sql_local + tep + seat_value;  //得到座位id，即座位值
        },
    );
    var ur = location.href;//获取地址
    var Cfilm_id = ur.split('?')[1].split('=')[1];
    if(!window.localStorage){
            alert("您还未登录！登陆后可使用该功能。");
            return false;
        }else{
            var storage=window.localStorage;
            //写入a字段
            storage["sql_local"]=sql_local;
            storage["total"]=total;
            storage["Cfilm_id"]=Cfilm_id;
        }
}

function insert(){
    var storage=window.localStorage;
    var Cfilm_id=storage["Cfilm_id"];
    var sql_local=storage["sql_local"];
    var post_data = {"Cfilm_id": Cfilm_id, "sql_local": sql_local};
    $.ajax({
        url: "/myapp/insertseat/",
        type: 'POST',
        data: post_data,
        success: function () {
            $.ajax({
            url: "/myapp/addOrder/",
            type: 'POST',
            data: post_data,
            success: function (Order_info) {
                order_id = JSON.parse(Order_info).Order_info.Order_id;
                order_Movie_name = JSON.parse(Order_info).Order_info.Cfilm_Movie_name;
                order_Cflim_date = JSON.parse(Order_info).Order_info.Order_date;
                order_Cflim_local = JSON.parse(Order_info).Order_info.Order_local;
                Cinema_name = JSON.parse(Order_info).Order_info.Cinema_name;
                Cinema_address = JSON.parse(Order_info).Order_info.Cinema_address;
                Cinema_phone = JSON.parse(Order_info).Order_info.Cinema_phone;
                Order_number = JSON.parse(Order_info).Order_info.Order_number;
                Cfilm_price = JSON.parse(Order_info).Order_info.Cfilm_price;
                var order_Cflim_local = order_Cflim_local.split('#').slice(1,);
                document.getElementById("order_id").innerHTML=order_id;
                document.getElementById("order_date").innerHTML=order_Cflim_date;
                document.getElementById("order_Movie_name").innerHTML=order_Movie_name;
                document.getElementById("order_Cflim_local").innerHTML=order_Cflim_local;
                document.getElementById("order_Cinema_name").innerHTML=Cinema_name;
                document.getElementById("cinema_name_").innerHTML=Cinema_address;
                document.getElementById("cinema_address_").innerHTML=Cinema_phone;
                document.getElementById("total_price").innerHTML=Number(Order_number)*Number(Cfilm_price);

            },
            error: function () {
            alert("服务器请求超时!");
        }
    })
        },
        error: function () {
            alert("服务器请求超时,请重试!");
        }
    })
}





