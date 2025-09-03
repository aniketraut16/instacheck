chrome.action.onClicked.addListener(t=>{if(t.id&&t.url){if(["chrome://","chrome-extension://","moz-extension://","edge://","about:","data:","file://"].some(e=>t.url.startsWith(e))){console.log("Cannot inject content script into restricted URL:",t.url);return}if(!(t.url.includes("instagram.com/reels/")||t.url.includes("instagram.com/reel/"))){chrome.scripting.executeScript({target:{tabId:t.id},func:()=>{const e=document.createElement("div");e.id="insta-check-notification",e.style.cssText=`
              position: fixed;
              top: 20px;
              right: 20px;
              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              color: white;
              padding: 16px 20px;
              border-radius: 12px;
              box-shadow: 0 10px 25px rgba(0,0,0,0.2);
              z-index: 999999;
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
              font-size: 14px;
              font-weight: 500;
              max-width: 300px;
              border: 2px solid rgba(255,255,255,0.2);
              backdrop-filter: blur(10px);
              animation: slideIn 0.3s ease-out;
            `,e.innerHTML=`
              <div style="display: flex; align-items: center; gap: 12px;">
                <div style="
                  width: 24px;
                  height: 24px;
                  background: rgba(255,255,255,0.2);
                  border-radius: 50%;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  font-size: 16px;
                ">⚠️</div>
                <div>
                  <div style="font-weight: 600; margin-bottom: 4px;">Insta Check</div>
                  <div style="font-size: 12px; opacity: 0.9;">
                    This extension only works on Instagram Reels pages!
                  </div>
                </div>
              </div>
              <button id="close-notification" style="
                position: absolute;
                top: 8px;
                right: 8px;
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                font-size: 16px;
                opacity: 0.7;
                padding: 4px;
                border-radius: 4px;
              ">×</button>
            `;const i=document.createElement("style");i.textContent=`
              @keyframes slideIn {
                from {
                  transform: translateX(100%);
                  opacity: 0;
                }
                to {
                  transform: translateX(0);
                  opacity: 1;
                }
              }
            `,document.head.appendChild(i);const o=document.getElementById("insta-check-notification");o&&o.remove(),document.body.appendChild(e),e.querySelector("#close-notification")?.addEventListener("click",()=>{e.style.animation="slideIn 0.3s ease-out reverse",setTimeout(()=>e.remove(),300)}),setTimeout(()=>{e.parentNode&&(e.style.animation="slideIn 0.3s ease-out reverse",setTimeout(()=>e.remove(),300))},5e3)}}).catch(e=>{console.error("Failed to show notification:",e)});return}chrome.scripting.executeScript({target:{tabId:t.id},func:()=>{const e=document.getElementById("my-extension-sidebar"),i=document.getElementById("my-extension-page");i&&i.style.width==="100%"&&(e&&(e.style.display="block"),i&&(i.style.width="75%"))}}).catch(e=>{console.error("Failed to toggle sidebar:",e)}),chrome.scripting.executeScript({target:{tabId:t.id},files:["content.js"]}).catch(e=>{console.error("Failed to inject content script:",e)})}});
