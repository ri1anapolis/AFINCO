(()=>{var e={383:e=>{e.exports=()=>new Promise((e=>{window.addEventListener("DOMContentLoaded",(t=>{setTimeout((()=>{console.log("resolve"),e()}),100)}))}))},435:e=>{const t=(e,t,n)=>o=>{const s=o.key;if(e.includes(s)){const e=document.querySelector(t);n.value=e.textContent}};e.exports={handleClickEvent:(e,n)=>o=>{const s=o.target;if([s.hasAttribute("aria-owns"),s.parentElement.hasAttribute("aria-owns")].some((e=>!!e))){const o=document.querySelector(e.pseudoInputEl);o.addEventListener("keydown",t(n,e.pseudoItemListEl,o))}},handleKeyDownEvent:t}}},t={};function n(o){if(t[o])return t[o].exports;var s=t[o]={exports:{}};return e[o](s,s.exports,n),s.exports}(()=>{const e=n(383),{handleClickEvent:t}=n(435);(async(n,o)=>{await e();const s=document.querySelector(n.pseudoSelectEl);s.addEventListener("click",t(n,o)),s.parentElement.addEventListener("click",t(n,o))})({pseudoSelectEl:"span.selection>span.select2-selection>span#select2-id_identificacao-container",pseudoInputEl:"span.select2-search--dropdown>input.select2-search__field",pseudoItemListEl:"li.select2-results__option--highlighted"},["ArrowRight","ArrowLeft"])})()})();