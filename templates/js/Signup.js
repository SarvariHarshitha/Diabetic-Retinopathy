function validation() {
    if(document.Formfill.username.value == "") {
        document.getElementById("result").textContent = "Enter Username*";
        return false;
    }
    else if(document.Formfill.email.value == "") {
        document.getElementById("result").textContent = "Enter Email*";
        return false;
    }
    else if(document.Formfill.password.value == "") {
        document.getElementById("result").textContent = "Enter Password*";
        return false;
    }
    else if(document.Formfill.password.value.length < 5) {
        document.getElementById("result").textContent = "Password Length should be >= 5*";
        return false;
    }
    else if(document.Formfill.cpassword.value == "") {
        document.getElementById("result").textContent = "Enter Confirm Password*";
        return false;
    }
    else if(document.Formfill.cpassword.value !=document.Formfill.password.value) {
        document.getElementById("result").textContent = "Password does'nt match*";
        return false;
    }
    else if(document.Formfill.cpassword.value == document.Formfill.password.value) {
        popup.classList.add("open-slide");
        return false;
    }

}

var popup = document.getElementById("popup");
function close() {
    popup.classList.add("open-slide");
}