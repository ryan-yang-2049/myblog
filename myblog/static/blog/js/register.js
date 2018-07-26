$(function () {
    $("#avatar").change(function () {
        var file_obj = $(this)[0].files[0];

        var reader = new FileReader();
        reader.readAsDataURL(file_obj);

        reader.onload = function () {
            $("#avatar_img").attr("src",reader.result)
        }

    });



    $(".reg_btn").click(function () {
        // 获取注册信息
        var formdata = new FormData();

        //serializeArray() 方法通过序列化表单值来创建对象数组（名称和值）。
        var request_data = $("#form").serializeArray();
        $.each(request_data,function (index,data) {
            formdata.append(data.name,data.value)
        });
        formdata.append("avatar",$("#avatar")[0].files[0]);

        $.ajax({
                url:"",
                type:"post",
                contentType:false,
                processData:false,
                data:formdata,
                success:function (data) {
                    if(data.user_info){
                        location.href = "/login/"
                    }else {
                        console.log(data.msg);
                        $("span.error").html("");
                        $(".form-group").removeClass("has-error");
                        $.each(data.msg,function (filed,error_list) {

                            if(filed === "__all__"){
                                $("#id_re_pwd").next().html(error_list[0]).parent().addClass("has-error")
                            }else {
                                $("#id_"+filed).next().html(error_list[0]).parent().addClass("has-error")
                            }

                        })
                    }
                }
            }
        );

    })

})