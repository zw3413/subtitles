export const addInjectScript = ()=>{
    var s1 = document.createElement('script');
    s1.src = chrome.runtime.getURL('subtitlexscript.js');
    s1.onload = function() { this.remove(); };
    (document.head || document.documentElement).appendChild(s1);
}