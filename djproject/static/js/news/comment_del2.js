function del(e) {

    // let $del_comment = $('.del_btn');
    // $del_comment.click(function () {
    let scomment_id = $(e).attr('comment-id');
    let news_id = $(e).attr('news-id');
    let _this = e;
    $.ajax({
        url: '/news/comments/' + news_id + '/' + scomment_id + '/del/',
        type: 'GET',
        dataType: "json",
    })
        .done(function (res) {
            if (res.errno === '0') {

                $(_this).parent().remove();

                message.showSuccess(res.errmsg);
                $('.comment-count').html(res.data.ccount);
            } else {
                message.showError(res.errmsg)
            }

        })
        .fail(function () {
            message.showError('服务器超时，请重试！');
        });

// });





}(jQuery);