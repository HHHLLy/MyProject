$(function () {





    let $upload_btn = $(".comment-form-wrap .form-group #upload_btn");
    let tag_btn = $(".tag-widget .tagcloud a");
    let $tag_display = $(".comment-form-wrap .form-group .tag_display");
    let img_btn = $(".comment-form-wrap .form-group #img_btn");
    let thumbnail_url = $(".comment-form-wrap .form-group #thumbnail_image");
    let current_url = $(".comment-form-wrap .form-group #current_image");
    let tag_id = "";
    let tag_name = "";
    tag_btn.click(function () {

        tag_id = $(this).prop("id");
        tag_name = $(this).html();
        if ($tag_display.find("a").length !== 0) {
            $tag_display.html("");
        }
        $tag_display.prepend(`<a href="javascript:void(0);" class="tag-cloud-link" id="${tag_id}">${tag_name} </a>`);


    });

    img_btn.click(function () {
        let file = $(".comment-form-wrap .form-group #image")[0].files[0];
        let oFormData = new FormData();
        oFormData.append("image_file", file);
        $.ajax(url = "/img_upload", {
            headers: {"X-CSRFToken": $.cookie("_xsrf")},
            method: "POST",
            data: oFormData,
            contentType: false,
            processData: false,
        })
            .done(function (res) {
                if (res.flag === "0") {

                    current_url.val(res.image_url);
                    thumbnail_url.val(res.thumbnail_url);
                    alert("上传成功");
                }
            })
            .fail(function () {
                alert("上传失败！");
            })
    });


    $upload_btn.click(function () {

        let $title = $(".comment-form-wrap .form-group #title").val();
        let $content = $(".comment-form-wrap .form-group #message").val();
        let display_tag_id = $(".comment-form-wrap .form-group .tag_display ").find("a").prop("id");

        if ($tag_display.find("a").length === 0) {
            alert("请选择标签");
            return
        }
        if ($title === "") {
            alert("请输入标题");
            return
        }
        if ($content === "") {
            alert("请输入内容");
            return
        }
        if (current_url.val() === "Please upload image.") {
            alert("请选择图片");
            return
        }





        let data = {
            "title":$title,
            "content":$content,
            "tag_id":display_tag_id,
            "image_url":current_url.val(),
            "thumbnail_url":thumbnail_url.val(),

        };
        $.ajax(url = "/upload", {
            headers: {"X-CSRFToken": $.cookie("_xsrf")},
            method: "POST",
            data: JSON.stringify(data),
            contentType: false,
            processData: false,
        })
            .done(function (res) {
                if (res.flag === "0") {
                    alert("上传成功");
                }else{
                    alert("无此用户");
                }
            })
            .fail(function () {
                alert("上传失败！");
            })
    });
});
