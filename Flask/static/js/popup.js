var popup = document.getElementsByClassName("popup");
var close = document.getElementsByClassName("popup-close");
var close_btn = document.getElementsByClassName("popup-close-btn");

var body = document.querySelector('body');

/*
for (i = 0; i < length(btn); i++) {
    btn[i].onclick = function () {
        popup[0].style.display = "block";
        body.style.overflow = "hidden";
    }
}*/



close[0].onclick = function () {
    popup[0].style.display = "none";
    body.style.overflow = "hidden";
};

close_btn[0].onclick = function () {
    popup[0].style.display = "none";
    body.style.overflow = "auto";
};

