function getweather() {
    function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      let cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        let cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  // Setting the token on the AJAX request
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      }
    }
  });
    let span_one = $('.span-one');
    span_one.text('加载中,请稍等');
    let city = $('#city').val();
    if (city === " "|| !city){
        message.showError('请输入正确城市名称');
        return
    }
    let SdataParams = {
        'city':city,
    };
    $.ajax({
        url: '/news/city/weather/',
        type: 'POST',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        data:JSON.stringify(SdataParams),
    })
        .done(function (res) {
            if (res.errno === "0") {
                let local_img = $('.local-img');
                let span_two = $('.span-two')
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
                _ul.html("");
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
                });
            }else {
              span_one.text("此城市不在查询范围");

            }
        })
        .fail(function () {
            message.showError('服务器超时，请重试！');
        });

};