var modal = document.getElementsByClassName('modal');
var btn = document.getElementsByClassName('modal_button');
var span = document.getElementsByClassName('close');

var body = document.querySelector('body');

console.log(modal);
console.log(btn);

/*
for (i = 0; i < modal.length; i++) {
    btn[i].onclick = function () {
        modal[i].style.display = "block";
        body.style.overflow = "hidden";
    };
    span[i].onclick = function () {
        modal[i].style.display = "none";
        body.style.overflow = "auto";
    };
}
*/

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

btn[2].onclick = function () {
    modal[2].style.display = "block";
    body.style.overflow = "auto";
};

span[2].onclick = function () {
    modal[2].style.display = "none";
    body.style.overflow = "auto";
};

window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
};