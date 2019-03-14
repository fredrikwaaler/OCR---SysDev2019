var modal = document.getElementsByClassName('modal');
var btn = document.getElementsByClassName('modal_button');
var span = document.getElementsByClassName('close');

var body = document.querySelector('body');

console.log(modal);

btn[0].onclick = function () {
    modal[0].style.display = "block";
    body.style.overflow = "hidden";
};

span[0].onclick = function () {
    modal[0].style.display = "none";
    body.style.overflow = "auto";
};

btn[1].onclick = function () {
    modal[1].style.display = "block";
    body.style.overflow = "hidden";
};

span[1].onclick = function () {
    modal[1].style.display = "none";
    body.style.overflow = "auto";

};

window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
} 