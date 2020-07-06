let ua = window.navigator.userAgent;
let msie = ua.indexOf("MSIE ");
let trident = ua.indexOf('Trident/');
if (msie > 0 || trident > 0 && window.location.href.indexOf("/ie") < 0) {
    window.location = "/ie";
}