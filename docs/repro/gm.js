window.GM_addStyle = function (css) {
  var s = document.createElement("style");
  s.textContent = css;
  document.head.appendChild(s);
};
window.GM_getValue = function (k, d) { return d; };
window.GM_setValue = function () {};
window.GM_info = { script: { name: "\u6d77\u5e95\u5c0f\u7eb5\u961f \u00b7 \u63a2\u77ff\u9cb8\u5a18", author: "X.H", namespace: "xinghong", version: "0.4.0", description: "d" } };
window.GM_xmlhttpRequest = function () {};
window.GM_getResourceText = function () { return ""; };
window.unsafeWindow = window;
