chrome.runtime.onInstalled.addListener(() => {
    // chrome.action.setBadgeText({
    //     text: "OFF"
    // })
})


chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.active) {
        chrome.scripting.executeScript({
            target: {tabId: tabId},
            func: addScript
        })
    }
})


// const extensions = 'https://developer.chrome.com/docs/extensions'
// const webstore = 'https://developer.chrome.com/docs/webstore'

const youtube = 'https://www.youtube.com'
const missav = 'https://missav.com'

chrome.action.onClicked.addListener(async(tab)=>{
//chrome.tabs.onActivated.addListener(async (tab) => {
    //console.log("action icon was clicked!")
    if (tab.url.startsWith(youtube) || tab.url.startsWith(missav)) {
        //Retrieve the action badge to check if the extension is 'ON' or 'OFF'
        const prevState = await chrome.action.getBadgeText({ tabId: tab.id });
        // Next state will always be the opposite
        const nextState = prevState === 'ON' ? 'OFF' : 'ON'

        //Set the action badge to the next state
        await chrome.action.setBadgeText({
            tabId: tab.id,
            text: nextState
        })

        if (nextState === 'ON') {
            //Insert the CSS file when the user turns the extension on
            await chrome.scripting.insertCSS({
                files: ["xpanel.css",
                "./subtitle/static/css/main.a1984400.chunk.css"],
                target: { tabId: tab.id }
            });
            await chrome.scripting.executeScript({
                target: {tabId: tab.id},
                func: addScript
            })
        } else if (nextState === 'OFF') {
            //Remove the CSS file when the user turns the extension off
            await chrome.scripting.removeCSS({
                files: ["focus-mode.css"],
                target: { tabId: tab.id }
            })
        }
    }
})


