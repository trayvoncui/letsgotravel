$(function () {
    var nav = $(".aside a");
    var con = $(".content>div");
    var s1 = null;
    var this1 = null;

    nav.click(function () {
        this1 = $(this);
        s1 = setTimeout(function () {
            var index = this1.index();
            nav.eq(index).addClass("style").siblings().removeClass("style");
            con.eq(index).show().siblings().hide();
        }, 2);
    });

    nav.mouseout(function () {
        clearTimeout(s1);
    })

    $("#image").change(function () {
        var file = this.files[0];
        if (window.FileReader) {
            var reader = new FileReader();
            reader.readAsDataURL(file);
            //监听文件读取结束后事件
            reader.onloadend = function (e) {
                $("#img").attr("src", e.target.result);    //e.target.result就是最后的路径地址
                //console.log(e.target.result);
            };
        }
    });

    $("#headimg").change(function () {
        var file = this.files[0];
        if (window.FileReader) {
            var reader = new FileReader();
            reader.readAsDataURL(file);
            //监听文件读取结束后事件
            reader.onloadend = function (e) {
                $("#img").attr("src", e.target.result);    //e.target.result就是最后的路径地址
                //console.log(e.target.result);
            };
        }
    });


})
