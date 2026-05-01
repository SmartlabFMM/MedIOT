(function () {
    "use strict";

    function patchLogout() {
        document.querySelectorAll('a[href*="/web/session/logout"]').forEach(function (a) {
            a.href = "/web/session/logout?redirect=/";
        });
    }

    patchLogout();
    setInterval(patchLogout, 1000);
})();
