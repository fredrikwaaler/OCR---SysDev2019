let modal = document.getElementsByClassName('modal');
let modal_button = document.getElementsByClassName('modal_button');
let span = document.getElementsByClassName('close');
let body = document.querySelector('body');

for (let btn = 0; btn < modal_button.length ; btn++) {
    if (modal_button[btn] != null) {
        modal_button[btn].onclick = function () {
            modal[btn].style.display = "block";
            body.style.overflow = "hidden";
        };
    }
    if (span[btn] != null) {
        span[btn].onclick = function () {
            modal[btn].style.display = "none";
            body.style.overflow = "auto";
        };
    }
}
/**
window.onclick = function(event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
};
*/

function mode_new_customer() {
    document.getElementById("new-customer").style.display = "grid";
}

function mode_new_supplier() {
    document.getElementById("new-customer").style.display = "none";
}

function test2() {
    let type = document.getElementById("account_type").value;
    if (type === "regular") {
        document.getElementById("foreign").style.display = "none";
    }
    if (type === "irregular") {
        document.getElementById("foreign").style.display = "grid";
    }
}