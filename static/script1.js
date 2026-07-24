// 获取按钮元素
var homeBtn = document.getElementById("home");
var overviewBtn = document.getElementById("overview");
var ageBtn = document.getElementById("age");
var heightBtn = document.getElementById("height");
var educationBtn = document.getElementById("education");
var wordcloudBtn = document.getElementById("wordcloud");
var wordcloudidBtn = document.getElementById("wordcloudid");

// 获取按钮点击后跳转的链接
var homeUrl = "../index";  // 主页链接
var overviewUrl = "../china";  // 全国总览链接
var ageUrl = "../china02";  // 全国总览链接
var heightUrl = "../china03";  // 全国总览链接
var educationUrl = "../china04";  // 全国总览链接
var wordcloudUrl = "../china05";  // 全国总览链接
var wordcloudidUrl = "../china06";  // 全国总览链接

// 为按钮添加点击事件监听器
homeBtn.addEventListener("click", function() {
        window.location.href = homeUrl;
});
overviewBtn.addEventListener("click", function() {
        window.location.href = overviewUrl;
});
ageBtn.addEventListener("click", function() {
        window.location.href = ageUrl;
});
heightBtn.addEventListener("click", function() {
        window.location.href = heightUrl;
});
educationBtn.addEventListener("click", function() {
        window.location.href = educationUrl;
});
wordcloudBtn.addEventListener("click", function() {
        window.location.href = wordcloudUrl;
});
wordcloudidBtn.addEventListener("click", function() {
        window.location.href = wordcloudidUrl;
});

