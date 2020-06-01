$(function () {
    let li = $("#colorlib-main-menu li");
    let loc_url = window.location.pathname;
    if("/upload" === loc_url){

        li.eq(6).addClass("colorlib-active").siblings().removeClass();
    }else if ("/" === loc_url){
        li.eq(0).addClass("colorlib-active").siblings().removeClass();
    }else if ("/photo" === loc_url){
        li.eq(1).addClass("colorlib-active").siblings().removeClass();
    }else if ("/travel" === loc_url){
        li.eq(2).addClass("colorlib-active").siblings().removeClass();
    }else if ("/fashion" === loc_url){
        li.eq(3).addClass("colorlib-active").siblings().removeClass();
    }else if ("/about" === loc_url){
        li.eq(4).addClass("colorlib-active").siblings().removeClass();
    }else if ("/contact" === loc_url){
        li.eq(5).addClass("colorlib-active").siblings().removeClass();
    }


    // $(this).addClass("colorlib-active");



});