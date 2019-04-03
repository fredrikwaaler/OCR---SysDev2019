let mdblock = document.getElementById("maturity_date-block");
let mdblock_filler = document.getElementById("maturity_date-block-filler");
let paid = document.getElementById("pf-paid");
let payment = document.getElementById("pf-payment");
let supplier = document.getElementById("supplier");
let supplier_button = document.getElementById("supplier-button");
let amount = document.getElementById("amount");

// MODE SELECTION

/**
 * Changes the mode to supplier mode.
 */
function mode_supplier() {
    mdblock.style.display = "grid";
    paid.style.display = "grid";
    payment.style.display = "none";
    supplier.disabled = false;
    supplier_button.disabled = false;
}

/**
 * Changes the mode to cash mode.
 */
function mode_cash() {
    mdblock.style.display = "none";
    paid.style.display = "none";
    payment.style.display = "grid";
    supplier.disabled = true;
    supplier_button.disabled = true;
}


// LINE SELECTION

let counter = 1; //Counter to represent amount of made lines

/**
 * Adds a new line to purchase form.
 */

function add_line() {
    let line = "<div class=\"pf-line-input\">\n" +
        "                    <h4 class=\"pf-header-hidden\"> Tekst</h4>\n" +
        "                    <input id=\"text-"+counter+"\" name=\"text-"+counter+"\" type=\"text\">\n" +
        "                </div>\n" +
        "                <div class=\"pf-line-input\">\n" +
        "                    <h4 class=\"pf-header-hidden\">Kostnadskonto</h4>\n" +
        "                    <select id=\"billing_account-"+ counter +"\" name=\"billing_account-" + counter + "\"></select>\n" +
        "                </div>\n" +
        "                <div class=\"pf-line-input\" onchange=\"change_net()\">\n" +
        "                    <h4 class=\"pf-header-hidden\">Bruttobeløp</h4>\n" +
        "                    <input id=\"gross_amount-" + counter + "\" name=\"gross_amount-"+counter+"\" type=\"number\">\n" +
        "                </div>\n" +
        "                <div class=\"pf-line-input\">\n" +
        "                    <h4 class=\"pf-header-hidden\">Mva</h4>\n" +
        "                    <select id=\"vat-"+counter+"\" name=\"vat-"+counter+"\"></select>\n" +
        "                </div>\n" +
        "                <div class=\"pf-line-input\">\n" +
        "                    <h4 class=\"pf-header-hidden\">Nettobeløp</h4>\n" +
        "                    <input id=\"net_amount-"+counter+"\" name=\"net_amount-"+counter+"\" type=\"number\">\n" +
        "                </div>\n" +
        "                <div class=\"pf-line-input\">\n" +
        "                    <input class=\"pf-button\" id=\"pf-button-"+counter+"\" type=\"button\" Value=\"Slett linje\" onclick=\"remove_line(this.parentNode.parentNode.id)\">\n" +
        "                </div>"
    let parent = "pf-lines";
    let element = "div";
    let element_id = "pf-line-"+counter;
    addElement(parent, "pf-line", element, element_id, line);
}

//add_line(); //Initialize with one line.

function addElement(parentId, elementClass, elementTag, elementId, html) {
    // Adds an element to the document
    let p = document.getElementById(parentId);
    let newElement = document.createElement(elementTag);
    newElement.setAttribute('class', elementClass);
    newElement.setAttribute('id', elementId);
    newElement.innerHTML = html;
    p.appendChild(newElement);
    counter++;
}


function remove_line(id) {
    let pf_lines = document.getElementById("pf-lines");
    if (pf_lines.children.length > 1){
        removeElement(id);
    } else {
        // TODO - Flash if only one element is left
        console.log("Cant remove line");
    }
}

function removeElement(elementId) {
    // Removes an element from the document
    let element = document.getElementById(elementId);
    if (element != null) {
        element.parentNode.removeChild(element);
    }
}


/**
 * Clears the purchase form for input and deletes lines.
 */
function clear_purchase_form() {
    document.getElementById("purchase-form").reset();
    for (let i = 1; i < counter; i++) {
        let id = "pf-line-"+i;
        remove_line(id);
    }
    counter =1;
}


let purchaseForm = document.getElementById("purchase-form");
function change_net(){
    // TODO - Change value of gross field when net field is changed.
    let gross_total = 0;
    let net_total = 0;
    for (let i = 1; i < counter; i++) {
        let gross_id = "gross_amount-" + i;
        let net_id = "net_amount-" + i;
        let gross_pointer = document.getElementById(gross_id);
        let net_pointer = document.getElementById(net_id);
        if (gross_pointer != null){
            let gross_amount = Number(gross_pointer.value);
            let net_amount = gross_amount/(1.25);
            net_pointer.value = net_amount;
            gross_total += gross_amount;
            net_total += net_amount;
        }
    }
    let vat_total = gross_total-net_total;
    change_total(gross_total, vat_total, net_total);
}

function change_total(gross_total, vat_total, net_total) {
    let total = document.getElementById("total-amount");
    let amount = document.getElementById("amount");
    total.innerHTML = "Totalbeløp: " + net_total.toFixed(2) + " + mva: " +
        vat_total.toFixed(2) +" = " +  gross_total.toFixed(2);
    amount.value = gross_total;
}

let product_line = `
<div class="description-column">
    <div class="sf-line-input">
        <select id="product-1" name="product-1"></select>
    </div>
    <div class="sf-line-input">
        <h4 class="sf-header-hidden">Kommentar</h4>
        <input id="sale_comment-1" name="sale_comment-1" type="text" placeholder="Kommentar (ikke påkrevd)">
    </div>
</div>
<div class="sf-line-input line-split">
    <h4 class="sf-header-hidden">Pris</h4>
    <input id="price-1" name="price-1" type="number">
</div>
<div class="sf-line-input line-split">
    <h4 class="sf-header-hidden">Rabatt</h4>
    <input id="discount-1" name="discount-1" type="number">
</div>
<div class="sf-line-input line-split">
    <h4 class="sf-header-hidden">Antall</h4>
    <input id="amount-1" name="amount-1" type="number" >
</div>
<div class="sf-line-input line-split">
    <h4 class="sf-header-hidden">Mva</h4>
    <select id="sale_vat-1" name="sale_vat-1"></select>
</div>
<div class="sf-line-input sf-line-button">
    <p class="sf-line-total" id="sf-line-total-1">1500.00</p>
    <input class="sf-button" id="sf-button-1" type="button" Value="Slett linje" onclick="remove_sale_line(this.parentNode.parentNode.id)">
</div>
<div class="sf-line-input">

</div>
`;

function add_product_line() {
    let id = "sf-line-" + counter;
    addElement("sf-lines", "sf-line", "div", id, product_line);
}

let freetext_line = `
<div class="description-column">
    <div class="sf-line-input">
        <h4 class="sf-header-hidden">Tekst</h4>
        <input id="description" name="description" type="text">
    </div>
    <ul class="sf-line-input" id="sale-type">
        <li>
            <input id="sale_type-0", name="sale_type" type="radio" value="1" checked="checked">
            <label for="sale_type-0">Vare (for videresalg)</label>
        </li>
        <li>
            <input id="sale_type-1", name="sale_type" type="radio" value="2">
            <label for="sale_type-1">Vare (egenprodusert)</label>
        </li>
        <li>
            <input id="sale_type-2", name="sale_type" type="radio" value="3">
            <label for="sale_type-2">Tjeneste</label>
        </li>
        <li>
        <input id="sale_type-3", name="sale_type" type="radio" value="4">
        <label for="sale_type-3">Annet</label>
        </li>
    </ul>
    <div class="sf-line-input">
        <h4 class="sf-header-hidden">Kommentar</h4>
        <input id="sale_comment-1" name="sale_comment-1" type="text">
    </div>
</div>
<div class="sf-line-input line-split">
    <h4 class="sf-header-hidden">Pris</h4>
    <input id="price-1" name="price-1" type="number">
</div>
<div class="sf-line-input line-split">
    <h4 class="sf-header-hidden">Rabatt</h4>
    <input id="discount-1" name="discount-1" type="number">
</div>
<div class="sf-line-input line-split">
    <h4 class="sf-header-hidden">Antall</h4>
    <input id="amount-1" name="amount-1" type="number">
</div>
<div class="sf-line-input line-split">
    <h4 class="sf-header-hidden">Mva</h4>
    <select id="sale_vat-1" name="sale_vat-1"></select>
</div>
<div class="sf-line-input sf-line-button">
    <p class="sf-line-total" id="sf-line-total-2">1500.00</p>
    <input class="sf-button" id="sf-button-1" type="button" Value="Slett linje" onclick="remove_sale_line(this.parentNode.parentNode.id)">
</div>
`;

function add_freetext_line() {
    let id = "sf-line-" + counter;
    addElement("sf-lines", "sf-line", "div", id, freetext_line);
}

function remove_sale_line(id) {
    let sf_lines = document.getElementById("sf-lines");
    if (sf_lines.children.length > 1){
        removeElement(id);
    } else {
        // TODO - Flash if only one element is left
        console.log("Cant remove line");
    }
}

function clear_sale_form() {
    document.getElementById("sale-form").reset();
    for (let i = 1; i < counter; i++) {
        let id = "sf-line-"+i;
        remove_sale_line(id);
    }
    counter =1;
}