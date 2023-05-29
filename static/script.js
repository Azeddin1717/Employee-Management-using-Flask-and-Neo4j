let btn4 = document.querySelector('#btn4')
btn4.addEventListener("click", function(){ confirm("Vous vouler supprimer ce employer ? "); });
document.getElementById("managers-link").addEventListener("click", function() {
    window.location.href = "manager.html";
});

document.getElementById("headers-link").addEventListener("click", function() {
    window.location.href = "headers.html";
});

document.getElementById("index-link").addEventListener("click", function() {
    window.location.href = "index.html";
});
