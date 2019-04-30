let inputs = document.getElementsByName("input");

for(let i=1; i < inputs.length; i++) {
    if (inputs[i].value === "") {
        inputs[i].style.border = "red";
    } else {
        inputs[i].style.border = "none";
    }
}