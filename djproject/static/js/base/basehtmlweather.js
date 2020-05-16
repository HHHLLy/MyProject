$(function () {

    $.ajax({
        url:'/news/weather/',
        type:'GET',
        dataType: "json",
    })
        .done(function (res) {
            if (res.errno === "0") {
                let local_img = $('.local-img');
                let span_one = $('.span-one');
                let span_two = $('.span-two');
                let _ul = $('.side-attention-address');
                let postion = $('.attention-span-one');
                let updatetime = $('.attention-span-two');
                let content_top = res.data.city + " " + res.data.today_weather.weather + " "
                    + res.data.today_weather.temphigh + '℃' + "/" + res.data.today_weather.templow + '℃';
                let content_bottom = res.data.today_weather.winddirect + " " + res.data.today_weather.windpower;
                local_img.attr("src",'/static/images/weathercn/'+res.data.today_weather.img+'.png');
                span_one.text(content_top);
                span_two.text(content_bottom);
                postion.text(res.data.city);
                updatetime.text(res.data.updatetime);
                var flg = 2;
                res.data.weather_list.forEach(function (one_weather) {

                    if(flg % 2 === 0){
                        flg = flg + 1;
                        let weatherhtml = `
                         <li style="background-color: white;">
                              <img src="/static/images/weathercn/${one_weather.img}.png">
                              <span style="left: 60px;">${one_weather.weather}</span>
                              <span style="left: 120px;">${one_weather.temphigh}℃/${one_weather.templow}℃</span>                       
                              <span style="right: 6px;">${one_weather.date}日(${one_weather.week})</span>
                          </li>
                    `;
                        _ul.append(weatherhtml);
                    }else{
                        flg = flg -1;
                        let weatherhtml = `
                         <li  style="background-color: #F0F0F0;">
                              <img src="/static/images/weathercn/${one_weather.img}.png">
                              <span style="left: 60px;">${one_weather.weather}</span>
                              <span style="left: 120px;">${one_weather.temphigh}℃/${one_weather.templow}℃</span>                       
                              <span style="right: 6px;">${one_weather.date}日(${one_weather.week})</span>
                          </li>
                    `;
                        _ul.append(weatherhtml);
                    }

                    // console.log(weatherhtml);

                });


            }else{
                span_one.text('查询失败，请稍后重试！');
            }
        })
        .fail(function () {
            message.showError('服务器超时，请重试！');
        });
});