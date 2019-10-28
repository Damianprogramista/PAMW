function init() {
    emailValidate();
    passwordValidate();
    confirmPasswordValidate();
    loginValidate();
    createAccount();
}

function emailValidate() {
    let email = document.getElementById('email')
    let errorMessage = document.createElement("small");
    errorMessage.style = "color: red";
    email.addEventListener('keyup', e => {
        regex = new RegExp("^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9.-]+\.[A-Z]{2,}$",
            'i', 'g', 'm')
        if (email.value.match(regex)) {
            email.classList.add('is-valid');
            email.classList.remove('is-invalid');
            if (email.parentNode.contains(errorMessage))
                email.parentNode.removeChild(errorMessage);
        }
        else {
            email.classList.remove('is-valid');
            email.classList.add('is-invalid');
            if (!email.value.length) {
                errorMessage.innerHTML = "Email cannot be empty"
            }
            else {
                errorMessage.innerHTML = "Invalid format";

            }
            email.parentNode.insertBefore(errorMessage, email.nextSibling)
        }
        
    })
}

function passwordValidate() {
    let password = document.getElementById('password');
    let errorMessage = document.createElement("small");
    errorMessage.style = "color: red";
    password.addEventListener('keyup', e => {
        if (password.value.length >= 8) {
            password.classList.add('is-valid');
            password.classList.remove('is-invalid');
            if (password.parentNode.contains(errorMessage)) {
                password.parentElement.removeChild(errorMessage);
            } 
        }
        else {
            password.classList.remove('is-valid');
            password.classList.add('is-invalid');
            if (!password.value.length) {
                errorMessage.innerHTML = "Password cannot be empty"
            }
            else {
                errorMessage.innerHTML = "Must have at least 8 characters";
            }
            password.parentNode.insertBefore(errorMessage, password.nextSibling)
        }
        
    })
}

function confirmPasswordValidate() {
    let password = document.getElementById('confirm-password');
    let errorMessage = document.createElement("small");
    errorMessage.style = "color: red";
    password.addEventListener('keyup', e => {
        if (password.value.length >= 8 
            && password.value === document.getElementById('password').value) {
            password.classList.add('is-valid');
            password.classList.remove('is-invalid');
            if (password.parentNode.contains(errorMessage)) {
                password.parentElement.removeChild(errorMessage);
            } 
        }
        else {
            password.classList.remove('is-valid');
            password.classList.add('is-invalid');
            if (!password.value.length) {
                errorMessage.innerHTML = "Password cannot be empty"
            }
            else if(password.value.length < 8 ){
                errorMessage.innerHTML = "Must have at least 8 characters";
            }
            else {
                errorMessage.innerHTML = "Password does not match";
            }
            password.parentNode.insertBefore(errorMessage, password.nextSibling)
        }
        
    })
}

function loginValidate() {
    let login = document.getElementById('login')
    let errorMessage = document.createElement("small");
    login.addEventListener('keyup', e => {
        if (login.value === '') {
            login.classList.remove('is-valid');
            login.classList.add('is-invalid');
            errorMessage.style = "color: red";
            errorMessage.innerHTML = "Login cannot be empty"
            login.parentNode.insertBefore(errorMessage, login.nextSibling)
        }
        else {
            fetch("http://localhost:3000/user/" + login.value)
            .then(resp => {
                console.log(resp.status)
                if (resp.status == 200) {
                    login.classList.remove('is-valid');
                    login.classList.add('is-invalid');
                    errorMessage.style = "color: red";
                    errorMessage.innerHTML = "Login already exists"
                }
                else {
                    login.classList.add('is-valid');
                    login.classList.remove('is-invalid');
                    errorMessage.style = "color: green";
                    errorMessage.innerHTML = "Login available"
                }
                login.parentNode.insertBefore(errorMessage, login.nextSibling)
    
            })
        }
        
    })

}
function createAccount() {
    let form  = document.getElementById('form')
    let message = document.createElement("small");
    form.addEventListener('submit', e => {
        e.preventDefault();
        anyInvalid = false;
        for (var i = 0; i < form.length-1; ++i) {
            form[i].dispatchEvent(new Event('keyup'))
            if(form[i].classList.contains('is-invalid'))
                anyInvalid = true;
        }
        if(anyInvalid)
            return;
        let formData = new FormData(form);
        for (var i = 0; i < form.length-2; ++i) {
            formData.append(form[i].name, form[i].value);
        }
        fetch("http://localhost:3000/register", {
            method: 'POST',
            body: formData,
        })
        .then(e => {
            message.style = "color: green"
            message.innerHTML = "Account created"
            form.parentNode.insertBefore(message, form.nextSibling)
        })
        .catch(e => {
            message.style = "color: red"
            message.innerHTML = "Something went wrong"
            form.parentNode.insertBefore(message, form.nextSibling)
        })
    })
}
