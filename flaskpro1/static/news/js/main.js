$(function(){

	// 打开登录框
	$('.login_btn').click(function(){
        $('.login_form_con').show();
	})
	
	// 点击关闭按钮关闭登录框或者注册框
	$('.shutoff').click(function(){
		$(this).closest('form').hide();
	})

    // 隐藏错误
    $(".login_form #mobile").focus(function(){
        $("#login-mobile-err").hide();
    });
    $(".login_form #password").focus(function(){
        $("#login-password-err").hide();
    });

    $(".register_form #mobile").focus(function(){
        $("#register-mobile-err").hide();
    });
    $(".register_form #imagecode").focus(function(){
        $("#register-image-code-err").hide();
    });
    $(".register_form #smscode").focus(function(){
        $("#register-sms-code-err").hide();
    });
    $(".register_form #password").focus(function(){
        $("#register-password-err").hide();
    });


	// 点击输入框，提示文字上移
	// $('.form_group').on('click focusin',function(){
	// 	$(this).children('.input_tip').animate({'top':-5,'font-size':12},'fast').siblings('input').focus().parent().addClass('hotline');
	// })
    //
	// // 输入框失去焦点，如果输入框为空，则提示文字下移
	// $('.form_group input').on('blur focusout',function(){
	// 	$(this).parent().removeClass('hotline');
	// 	var val = $(this).val();
	// 	if(val=='')
	// 	{
	// 		$(this).siblings('.input_tip').animate({'top':22,'font-size':14},'fast');
	// 	}
	// })

    // 点击输入框，提示文字上移
    $('.form_group').on('click',function(){
        $(this).children('input').focus()
    })

    // 输入框失去焦点，如果输入框为空，则提示文字下移
    $('.form_group input').on('focusin',function(){
        $(this).siblings('.input_tip').animate({'top':-5,'font-size':12},'fast')
        $(this).parent().addClass('hotline');
    })



	// 打开注册框
	$('.register_btn').click(function(){
		$('.register_form_con').show();
		generateImageCode()
	})


	// 登录框和注册框切换
	$('.to_register').click(function(){
		$('.login_form_con').hide();
		$('.register_form_con').show();
        generateImageCode()
	})

	// 登录框和注册框切换
	$('.to_login').click(function(){
		$('.login_form_con').show();
		$('.register_form_con').hide();
	})

	// 根据地址栏的hash值来显示用户中心对应的菜单
	var sHash = window.location.hash;
	if(sHash!=''){
		var sId = sHash.substring(1);
		var oNow = $('.'+sId);		
		var iNowIndex = oNow.index();
		$('.option_list li').eq(iNowIndex).addClass('active').siblings().removeClass('active');
		oNow.show().siblings().hide();
	}

	// 用户中心菜单切换
	var $li = $('.option_list li');
	var $frame = $('#main_frame');

	$li.click(function(){
		if($(this).index()==5){
			$('#main_frame').css({'height':900});
		}
		else{
			$('#main_frame').css({'height':660});
		}
		$(this).addClass('active').siblings().removeClass('active');
		$(this).find('a')[0].click()
	})

    // TODO 登录表单提交
    $(".login_form_con").submit(function (e) {
        e.preventDefault()
        var mobile = $(".login_form #mobile").val()
        var password = $(".login_form #password").val()

        if (!mobile) {
            $("#login-mobile-err").show();
            return;
        }

        if (!password) {
            $("#login-password-err").show();
            return;
        }
        var csrf_token = $("#csrf_token_login").val()
        // 发起登录请求
        var params = {
            "mobile": mobile,
            "password": password,
            "csrf_token":csrf_token
        }

        //发送登陆请求
        $.ajax({
            url:"/user/login",
            method: "post",
            data: params,
            dataType: "json",
            success: function (resp) {
            console.log(resp)
                if (resp.code == "200") {
                    // 刷新当前界面
                    location.reload();
                }else {
                    $("#login-password-err").html(resp.message)
                    $("#login-password-err").show()
                }
            }
        })
    })


    // TODO 注册按钮点击
    $(".register_form_con").submit(function (e) {
        // 阻止默认提交操作,不让表单自动刷新,不走action
        e.preventDefault()

		// 取到用户输入的内容
        var mobile = $("#register_mobile").val()
        var smscode = $("#imagecode").val()

        var password = $("#register_password").val()
        var csrf_token = $("#csrf_token").val()

		if (!mobile) {
            $("#register-mobile-err").show();
            return;
        }
        //验证手机号格式
        var reg =/^1[3,8,5]\d{9}$/
        if(!reg.test(mobile)){
            alert("用机格式不正确")
            return;
        }

        if (!smscode) {
            $("#register-image-code-err").show();
            return;
        }
        if (!password) {
            $("#register-password-err").html("请填写密码!");
            $("#register-password-err").show();
            return;
        }

		if (password.length < 6) {
            $("#register-password-err").html("密码长度不能少于6位");
            $("#register-password-err").show();
            return;
        }

        //获取是否同意协议
        var agree = $(".agree_input:checked").val()
        // 拼接请求参数
        var params = {
            "mobile":mobile,
            "sms_code":smscode,
            "password":password,
            "csrf_token":csrf_token,
            "agree":agree
        }
        console.log(params)
        // 发起注册请求

        $.ajax({
            url:"/user/register",
            type:'POST',
            data:params,
            dataType:'json',
            success:function(resp){
                console.log(resp)
                //判断是否注册成功
                if(resp.code == "200"){
                    //重新加载页面
                    location.reload()
                }else{
                    $("#register-password-err").html(resp.message)
                    $("#register-password-err").show()
                }
            }

        })



    })
})

//退出登陆
function logout() {
    $.ajax({
        url:"/user/logout",
        type: "post",
        contentType: "application/json",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        success: function (resp) {
            // 刷新当前界面
            location.reload();
        }
    })
}




var imageCodeId = ""
var preimageCodeId = ""
// TODO 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {

    //生成一个随机字符串uuid
    imageCodeId = generateUUID()

    //拼接请求路径,和一个字符串没有什么两样
    image_url = "/user/get_image?cur_id="+imageCodeId + "&pre_id="+preimageCodeId

    //将image_Url设置到img标签中src, IMG标签只要设置了里面的src属性,会自动去请求跟上的地址
    $(".get_pic_code").attr("src",image_url)

    // 记录上一次的uuid
    preimageCodeId = imageCodeId

}

// 发送短信验证码
function sendSMSCode() {
    // 校验参数，保证输入框有数据填写
    $(".get_code").removeAttr("onclick");
    var mobile = $("#register_mobile").val();
    if (!mobile) {
        $("#register-mobile-err").html("请填写正确的手机号！");
        $("#register-mobile-err").show();
        $(".get_code").attr("onclick", "sendSMSCode();");
        return;
    }
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err").html("请填写验证码！");
        $("#image-code-err").show();
        $(".get_code").attr("onclick", "sendSMSCode();");
        return;
    }

    // TODO 发送短信验证码
    // 拼接请求参数
    var params = {
        "mobile":mobile,
        "image_code":imageCode,
        "image_code_id":imageCodeId
    }

    // 发送请求
    $.ajax({
        url: "/passport/sms_code",
        type:"POST",
        data:JSON.stringify(params),
        contentType: "application/json",
        success: function (resp) {
            //判断是否请求成功
            if(resp.errno == "0"){
                //倒计时60秒
                num = 60;
                var t = setInterval(function () {
                    //判断倒计时是否结束
                    if(num == 1){
                        //清空定时器
                        clearInterval(t)

                        //重新设置
                         $(".get_code").attr("onclick","sendSMSCode()");
                         $(".get_code").html("点击获取验证码")

                    }else{
                        // 设置倒计时数字
                        num -= 1
                        $(".get_code").html(num+"秒")
                    }
                },1000)

            }else{
                //短信发送失败
                alert(resp.errmsg)// 提示
                generateImageCode() // 生成图片验证码
                $(".get_code").attr("onclick","sendSMSCode()"); //重新设置可以点击状态
            }
        }
    })

}

// 调用该函数模拟点击左侧按钮
function fnChangeMenu(n) {
    var $li = $('.option_list li');
    if (n >= 0) {
        $li.eq(n).addClass('active').siblings().removeClass('active');
        // 执行 a 标签的点击事件
        $li.eq(n).find('a')[0].click()
    }
}

// 一般页面的iframe的高度是660
// 新闻发布页面iframe的高度是900
function fnSetIframeHeight(num){
	var $frame = $('#main_frame');
	$frame.css({'height':num});
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}
