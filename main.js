const signinBtn=document.querySelector("#sign-in-btn");
const signupBtn=document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");

signupBtn.addEventListener('click',()=>{
    container.classList.add("sign-up-mode");
});

signinBtn.addEventListener('submit',()=>{
    container.classList.remove("sign-up-mode");
    window.location.href = "home.html";
});