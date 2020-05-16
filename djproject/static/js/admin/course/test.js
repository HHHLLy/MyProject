$(function () {
    let sdk = baidubce.sdk;
    let Bosclient = sdk.BosClient;
    const CONFIG = {
      endpoint: 'http://hlyhly3.bj.bcebos.com',	// 默认区域名
      credentials: {
        ak: '101d30b54b5443e0ba56f8147e1d8ac5',	 // 填写你的百度云中ak和sk
        sk: '1e45ad4b6cfd4699bb6f29620b52d84a'
    }
  };
  const CLIENT = new Bosclient(CONFIG);
  CLIENT.listBuckets()
      .then(function (respones) {
            console.log(respones.body);
      })
      .fail(function () {

      });
  // get cookie using jQuery
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
});