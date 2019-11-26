window.addEventListener("load", afterLoad);
var sendButton;

function afterLoad(){
    sendButton = document.getElementById("sendButton")
    sendButton.addEventListener("click", checkData);
    errorLoginData()
}

function errorLoginData(){
    var cookieValue = document.cookie.split('=')[1];
    if(cookieValue == "INVALIDATE" || cookieValue == "LOGGED_OUT") {
        messageLogin(cookieValue);
    }
}

function checkData(){
    let empty = false;
    let inputs = document.querySelectorAll(".fieldInput");
    if (inputs[0].value.length == 0 || inputs[1].value.length == 0)
    {
        messageLogin("EMPTY");
        event.preventDefault();
    }
}

function messageLogin(type)
{
    let parent = document.getElementById("title");
    if (parent.childElementCount > 0) {
        parent.removeChild(parent.children[0]);
    }
    let child = document.createElement("label");
    switch (type) {
        case "EMPTY":
            child.setAttribute("class", "error");
            child.innerHTML = "<br>Wypełnij wszystkie pola!";
            break;
        case "INVALIDATE":
            child.setAttribute("class", "error");
            child.innerHTML = "<br>Wprowadzono nieprawidłowy login i/lub hasło!";
            break;
        case "LOGGED_OUT":
            child.setAttribute("class", "info");
            child.innerHTML = "<br>Wylogowano poprawnie!";
            break;
    }
    parent.appendChild(child);
}