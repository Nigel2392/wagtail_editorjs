// Modified version of https://github.com/kaaaaaaaaaaai/editorjs-alignment-blocktune
(()=>{"use strict";var t={523:(t,e,n)=>{n.d(e,{A:()=>o});var i=n(601),r=n.n(i),s=n(314),a=n.n(s)()(r());a.push([t.id,".ce-tune-alignment--right {\n    text-align: right;\n}\n.ce-tune-alignment--center {\n    text-align: center;\n}\n.ce-tune-alignment--left {\n    text-align: left;\n}",""]);const o=a},314:t=>{t.exports=function(t){var e=[];return e.toString=function(){return this.map((function(e){var n="",i=void 0!==e[5];return e[4]&&(n+="@supports (".concat(e[4],") {")),e[2]&&(n+="@media ".concat(e[2]," {")),i&&(n+="@layer".concat(e[5].length>0?" ".concat(e[5]):""," {")),n+=t(e),i&&(n+="}"),e[2]&&(n+="}"),e[4]&&(n+="}"),n})).join("")},e.i=function(t,n,i,r,s){"string"==typeof t&&(t=[[null,t,void 0]]);var a={};if(i)for(var o=0;o<this.length;o++){var c=this[o][0];null!=c&&(a[c]=!0)}for(var l=0;l<t.length;l++){var h=[].concat(t[l]);i&&a[h[0]]||(void 0!==s&&(void 0===h[5]||(h[1]="@layer".concat(h[5].length>0?" ".concat(h[5]):""," {").concat(h[1],"}")),h[5]=s),n&&(h[2]?(h[1]="@media ".concat(h[2]," {").concat(h[1],"}"),h[2]=n):h[2]=n),r&&(h[4]?(h[1]="@supports (".concat(h[4],") {").concat(h[1],"}"),h[4]=r):h[4]="".concat(r)),e.push(h))}},e}},601:t=>{t.exports=function(t){return t[1]}},72:t=>{var e=[];function n(t){for(var n=-1,i=0;i<e.length;i++)if(e[i].identifier===t){n=i;break}return n}function i(t,i){for(var s={},a=[],o=0;o<t.length;o++){var c=t[o],l=i.base?c[0]+i.base:c[0],h=s[l]||0,d="".concat(l," ").concat(h);s[l]=h+1;var u=n(d),p={css:c[1],media:c[2],sourceMap:c[3],supports:c[4],layer:c[5]};if(-1!==u)e[u].references++,e[u].updater(p);else{var g=r(p,i);i.byIndex=o,e.splice(o,0,{identifier:d,updater:g,references:1})}a.push(d)}return a}function r(t,e){var n=e.domAPI(e);return n.update(t),function(e){if(e){if(e.css===t.css&&e.media===t.media&&e.sourceMap===t.sourceMap&&e.supports===t.supports&&e.layer===t.layer)return;n.update(t=e)}else n.remove()}}t.exports=function(t,r){var s=i(t=t||[],r=r||{});return function(t){t=t||[];for(var a=0;a<s.length;a++){var o=n(s[a]);e[o].references--}for(var c=i(t,r),l=0;l<s.length;l++){var h=n(s[l]);0===e[h].references&&(e[h].updater(),e.splice(h,1))}s=c}}},659:t=>{var e={};t.exports=function(t,n){var i=function(t){if(void 0===e[t]){var n=document.querySelector(t);if(window.HTMLIFrameElement&&n instanceof window.HTMLIFrameElement)try{n=n.contentDocument.head}catch(t){n=null}e[t]=n}return e[t]}(t);if(!i)throw new Error("Couldn't find a style target. This probably means that the value for the 'insert' parameter is invalid.");i.appendChild(n)}},540:t=>{t.exports=function(t){var e=document.createElement("style");return t.setAttributes(e,t.attributes),t.insert(e,t.options),e}},56:(t,e,n)=>{t.exports=function(t){var e=n.nc;e&&t.setAttribute("nonce",e)}},825:t=>{t.exports=function(t){if("undefined"==typeof document)return{update:function(){},remove:function(){}};var e=t.insertStyleElement(t);return{update:function(n){!function(t,e,n){var i="";n.supports&&(i+="@supports (".concat(n.supports,") {")),n.media&&(i+="@media ".concat(n.media," {"));var r=void 0!==n.layer;r&&(i+="@layer".concat(n.layer.length>0?" ".concat(n.layer):""," {")),i+=n.css,r&&(i+="}"),n.media&&(i+="}"),n.supports&&(i+="}");var s=n.sourceMap;s&&"undefined"!=typeof btoa&&(i+="\n/*# sourceMappingURL=data:application/json;base64,".concat(btoa(unescape(encodeURIComponent(JSON.stringify(s))))," */")),e.styleTagTransform(i,t,e.options)}(e,t,n)},remove:function(){!function(t){if(null===t.parentNode)return!1;t.parentNode.removeChild(t)}(e)}}}},113:t=>{t.exports=function(t,e){if(e.styleSheet)e.styleSheet.cssText=t;else{for(;e.firstChild;)e.removeChild(e.firstChild);e.appendChild(document.createTextNode(t))}}}},e={};function n(i){var r=e[i];if(void 0!==r)return r.exports;var s=e[i]={id:i,exports:{}};return t[i](s,s.exports,n),s.exports}n.n=t=>{var e=t&&t.__esModule?()=>t.default:()=>t;return n.d(e,{a:e}),e},n.d=(t,e)=>{for(var i in e)n.o(e,i)&&!n.o(t,i)&&Object.defineProperty(t,i,{enumerable:!0,get:e[i]})},n.o=(t,e)=>Object.prototype.hasOwnProperty.call(t,e),n.nc=void 0,(()=>{var t=n(72),e=n.n(t),i=n(825),r=n.n(i),s=n(659),a=n.n(s),o=n(56),c=n.n(o),l=n(540),h=n.n(l),d=n(113),u=n.n(d),p=n(523),g={};function m(t,e="",n={}){const i=document.createElement(t);Array.isArray(e)?i.classList.add(...e):e&&i.classList.add(e);for(const t in n)i[t]=n[t];return i}g.styleTagTransform=u(),g.setAttributes=c(),g.insert=a().bind(null,"head"),g.domAPI=r(),g.insertStyleElement=h(),e()(p.A,g),p.A&&p.A.locals&&p.A.locals;class f{constructor({api:t,data:e,config:n,block:i}){this.api=t,this.block=i,this.settings=n,this.data=e||{alignment:this.getAlignment()},this.alignmentSettings=[{name:"left",icon:'<svg xmlns="http://www.w3.org/2000/svg" id="Layer" enable-background="new 0 0 64 64" height="20" viewBox="0 0 64 64" width="20"><path d="m54 8h-44c-1.104 0-2 .896-2 2s.896 2 2 2h44c1.104 0 2-.896 2-2s-.896-2-2-2z"/><path d="m54 52h-44c-1.104 0-2 .896-2 2s.896 2 2 2h44c1.104 0 2-.896 2-2s-.896-2-2-2z"/><path d="m10 23h28c1.104 0 2-.896 2-2s-.896-2-2-2h-28c-1.104 0-2 .896-2 2s.896 2 2 2z"/><path d="m54 30h-44c-1.104 0-2 .896-2 2s.896 2 2 2h44c1.104 0 2-.896 2-2s-.896-2-2-2z"/><path d="m10 45h28c1.104 0 2-.896 2-2s-.896-2-2-2h-28c-1.104 0-2 .896-2 2s.896 2 2 2z"/></svg>'},{name:"center",icon:'<svg xmlns="http://www.w3.org/2000/svg" id="Layer" enable-background="new 0 0 64 64" height="20" viewBox="0 0 64 64" width="20"><path d="m54 8h-44c-1.104 0-2 .896-2 2s.896 2 2 2h44c1.104 0 2-.896 2-2s-.896-2-2-2z"/><path d="m54 52h-44c-1.104 0-2 .896-2 2s.896 2 2 2h44c1.104 0 2-.896 2-2s-.896-2-2-2z"/><path d="m46 23c1.104 0 2-.896 2-2s-.896-2-2-2h-28c-1.104 0-2 .896-2 2s.896 2 2 2z"/><path d="m54 30h-44c-1.104 0-2 .896-2 2s.896 2 2 2h44c1.104 0 2-.896 2-2s-.896-2-2-2z"/><path d="m46 45c1.104 0 2-.896 2-2s-.896-2-2-2h-28c-1.104 0-2 .896-2 2s.896 2 2 2z"/></svg>'},{name:"right",icon:'<svg xmlns="http://www.w3.org/2000/svg" id="Layer" enable-background="new 0 0 64 64" height="20" viewBox="0 0 64 64" width="20"><path d="m54 8h-44c-1.104 0-2 .896-2 2s.896 2 2 2h44c1.104 0 2-.896 2-2s-.896-2-2-2z"/><path d="m54 52h-44c-1.104 0-2 .896-2 2s.896 2 2 2h44c1.104 0 2-.896 2-2s-.896-2-2-2z"/><path d="m54 19h-28c-1.104 0-2 .896-2 2s.896 2 2 2h28c1.104 0 2-.896 2-2s-.896-2-2-2z"/><path d="m54 30h-44c-1.104 0-2 .896-2 2s.896 2 2 2h44c1.104 0 2-.896 2-2s-.896-2-2-2z"/><path d="m54 41h-28c-1.104 0-2 .896-2 2s.896 2 2 2h28c1.104 0 2-.896 2-2s-.896-2-2-2z"/></svg>'}],this._CSS={alignment:{left:"ce-tune-alignment--left",center:"ce-tune-alignment--center",right:"ce-tune-alignment--right"}}}static get DEFAULT_ALIGNMENT(){return"left"}static get isTune(){return!0}getAlignment(){var t,e;return window.AlignmentEditorDirection?window.AlignmentEditorDirection:(null===(t=this.settings)||void 0===t?void 0:t.blocks)&&this.settings.blocks.hasOwnProperty(this.block.name)?this.settings.blocks[this.block.name]:(null===(e=this.settings)||void 0===e?void 0:e.default)?this.settings.default:f.DEFAULT_ALIGNMENT}wrap(t){return this.wrapper=m("div"),this.wrapper.classList.toggle(this._CSS.alignment[this.data.alignment]),this.wrapper.append(t),this.wrapper}render(){console.log("render");const t=m("div");return this.alignmentSettings.map((e=>{const n=document.createElement("button");return n.classList.add(this.api.styles.settingsButton),n.innerHTML=e.icon,n.type="button",n.classList.toggle(this.api.styles.settingsButtonActive,e.name===this.data.alignment),this.api.tooltip.onHover(n,this.api.i18n.t(`Align ${e.name}`),{placement:"top",offset:5}),t.appendChild(n),n})).forEach(((t,e,n)=>{t.addEventListener("click",(()=>{const t=this.alignmentSettings[e].name;this.data={alignment:t},window.AlignmentEditorDirection=t,n.forEach(((t,e)=>{const{name:n}=this.alignmentSettings[e];t.classList.toggle(this.api.styles.settingsButtonActive,n===this.data.alignment),this.wrapper.classList.toggle(this._CSS.alignment[n],n===this.data.alignment)})),this.block.dispatchChange()}))})),t}save(){return this.data}}window.AlignmentEditorDirection||(window.AlignmentEditorDirection="left",window.AlignmentBlockTune=f)})()})();