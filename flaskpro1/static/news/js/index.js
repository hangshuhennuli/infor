var currentCid = 1; // 当前分类 id
var cur_page = 1; // 当前页
var total_page = 1;  // 总页数
var house_data_querying = true;   // 是否正在向后台获取数据


$(function () {

    //调用方法回去数据
    updateNewsData()

    // 首页分类切换
    $('.menu li').click(function () {
        //获取分类编号
        var clickCid = $(this).attr('data-cid')
        //上个分类选择状态移除
        $('.menu li').each(function () {
            $(this).removeClass('active')
        })
        //将当前选中的分类置为选中状态
        $(this).addClass('active')

        //判断当前是否点击的不是当前编号
        if (clickCid != currentCid) {
            // 记录当前分类id
            currentCid = clickCid

            // 重置分页参数
            cur_page = 1
            total_page = 1
            updateNewsData()
        }
    })

    //页面滚动加载相关
    $(window).scroll(function () {

        // 浏览器窗口高度
        var showHeight = $(window).height();

        // 整个网页的高度
        var pageHeight = $(document).height();

        // 页面可以滚动的距离
        var canScrollHeight = pageHeight - showHeight;

        // 页面滚动了多少,这个是随着页面滚动实时变化的
        var nowScroll = $(document).scrollTop();

        if ((canScrollHeight - nowScroll) < 100) {
            // TODO 判断页数，去更新新闻数据
            if (!house_data_querying) {
            // 将`是否正在向后端查询新闻数据`的标志设置为真
            house_data_querying = true;
            // 如果当前页面数还没到达总页数
            if(cur_page < total_page) {
                // 向后端发送请求，查询下一页新闻数据
                updateNewsData();
            } else {
                house_data_querying = false;
            }
        }
        }
    })
})

// function updateNewsData1() {
//     // TODO 更新新闻数据
//     var params = {
//         "page": cur_page,
//         "cid": currentCid,
//     }
//     $.get("/getnewslist", params, function (resp) {

//         // 设置 `数据正在查询数据` 变量为 false，以便下次上拉加载
//         house_data_querying = false

//         if (resp) {

//             // 记录总页数
//             total_page = resp.totalPage

//             // 如果当前页数为1，则清空原有数据
//             if (cur_page == 1) {
//                 $(".list_con").html('')
//             }
//             // 当前页数递增
//             cur_page += 1
//             // 显示数据
//             for (var i=0;i<resp.mes.newsList.length;i++) {
//                 var news = resp.mes.newsList[i]
//                 var content = '<li>'
//                 content += '<a href="/news/'+news.id+'" class="news_pic fl"><img src="' + news.image_url + '"></a>'
//                 content += '<a href="/news/'+news.id+'" class="news_title fl">' + news.name + '</a>'
//                 content += '<a href="/news/'+news.id+'" class="news_detail fl">' + news.descrp + '</a>'
//                 content += '<div class="author_info fl">'
//                 // content += '<div class="source fl">来源：' + news.source + '</div>'
//                 content += '<div class="time fl">' + news.create_time + '</div>'
//                 content += '</div>'
//                 content += '</li>'
//                 $(".list_con").append(content)
//             }
//         }
//     })
// }

function updateNewsData(){
    var params = {'cid':currentCid,'page':cur_page}
    if (cur_page == 1){
        $(".list_con").html('')
    }
    $.ajax({
        url:'/getnewslist',
        type:'get',
        dataType:'json',
        data:params,
        success:function(res){
            //当前页数递增
            cur_page += 1
            //记录总页数
            total_page = res.total_page
            if(res.code == 200){
                var mes = res.newslist
                var len = mes.length
                var html = ''
                if (len>0){
                    for(var i=0;i<len;i++){
                        html+="<li><a href='' class='news_pic fl'><img src='"+mes[i]['image_url']+"'></a><a href='/detail?id="+mes[i]['id']+"' class='news_title fl'>"+mes[i]['name']+"</a>"+"<a href='' class='news_detail fl'>"+mes[i]['descrp']+"</a><div"+"class='author_info fl'>"+"<div class='time fl'>"+mes[i]['create_time']+"</div></div></li>"
                    }
                }
                $(".list_con").append(html)
            }
        }
    })
}