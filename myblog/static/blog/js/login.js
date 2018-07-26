$(function () {
    // 刷新验证码
    $("#valid_code_img").click(function () {
        // 相当于  http://127.0.0.1:8010/get_validCode_img/?   相当于发了一个get请求
        $(this)[0].src +="?"
    });
    $(".login_btn").click(function () {
        $.ajax({
            url:"",
            type:"post",
            data:{
                user:$("#user").val(),
                pwd:$("#pwd").val(),
                valid_code:$("#valid_code").val(),
                csrfmiddlewaretoken:$("[name='csrfmiddlewaretoken']").val()
            },
            success:function (data) {
                if(data.user){
                    location.href = "/index/"
                }else{
                    $("span.error").text(data.msg).css({"color":"red","margin-left":"10px"});
                    setTimeout(function () {
                        $("span.error").text("")
                    },2000)
                }
            }
        })
    });
});