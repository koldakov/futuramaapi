var FuturamaAPICookieName = "FuturamaAPI_CookieAccepted";
var cookieBannerId = "futurama-api-cookie-banner"

function showCookieBanner(){
    let cookieBanner = document.getElementById(cookieBannerId);
    cookieBanner.style.display = "block";
}

function hideCookieBanner(){
    localStorage.setItem(FuturamaAPICookieName, true);

    let cookieBanner = document.getElementById(cookieBannerId);
    cookieBanner.style.display = "none";
}

function initializeCookieBanner(){
    if(localStorage.getItem(FuturamaAPICookieName) === null) {
        showCookieBanner();
    }
}

window.onload = initializeCookieBanner();
window.futuramaapi_hideCookieBanner = hideCookieBanner;
