(function () {
    $.ajax({
        url:'/news/basehtmlcourse/',
        type:'GET',
        dataType: "json",
    })
        .done(function (res) {

            if (res.errno === "0") {
                let hotnewshtml = ``;

                $('.video').html(`<source  class='video_url' src="${res.data.video_url}" type="video/mp4">`);
                $('.activities-tips').text(`${res.data.title}`);
                res.data.hotnews_list.forEach(function (one_news) {
                    hotnewshtml += `
                <li>
                      <a href="/news/${one_news.id}/" class="hot-news-contain clearfix">
                          <div class="hot-news-thumbnail">
                              <img src="${one_news.image_url}"
                                   alt="">
                          </div>
                          <div class="hot-news-content">
                              <p class="hot-news-title">${one_news.title}</p>
                              <div class="hot-news-other clearfix">
                                  <span class="news-type">${one_news.tag_name}</span>
                                  <!-- 自带的 -->
                                  <time class="news-pub-time">${one_news.update_time}</time>
                                  <span class="news-author">${one_news.author}</span>
                              </div>
                          </div>
                      </a>
                  </li>    
                `
                });
                $('.hot-news-list').append(hotnewshtml);



            }else{
                 $('.activities-tips').html("<p>暂无最新视频</p>");
                  $('.hot-news-list').val('');
            }


        })
        .fail(function () {
            message.showError('服务器超时，请重试！');
        });
})(jQuery);