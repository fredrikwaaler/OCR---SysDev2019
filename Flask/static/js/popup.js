let popup = document.getElementsByClassName("popup");
let close = document.getElementsByClassName("popup-close");
let close_btn = document.getElementsByClassName("popup-close-btn");

// If there is a popup, noscroll for body
if (popup.length > 0) {
    document.body.style.overflow = "hidden";
}

if (!isEmpty(close)) {
    close[0].onclick = function () {
    popup[0].style.display = "none";
    document.body.style.overflow = "auto";
    }
}

if (!isEmpty(close_btn)) {
    close_btn[0].onclick = function () {
    popup[0].style.display = "none";
    document.body.style.overflow = "auto";
    };
}

function isEmpty(obj) {
    for(let key in obj) {
        if(obj.hasOwnProperty(key))
            return false;
    }
    return true;
}