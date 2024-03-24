const subtitlexserver = "https://api.subtitlex.xyz"
const youtube = 'https://www.youtube.com'
const missav = 'https://missav.com'
const supportWebsites = [youtube, missav]
var seedId,seedObj,tabUrl,processStatus 

document.addEventListener('DOMContentLoaded', (loadEvent) => {

    document.getElementById("wantSubtitle").addEventListener('click', async (e) => {
        console.log('wantSubtitle buttun was clicked.')
        console.log(seedId)
        let wantLang = document.getElementById("want_lang").value
        // info.want_language = wantLang + "&&" + userLanguage
        // let url_want = subtitlexserver+"/want_subtitle"
        // let xhr_want = new XMLHttpRequest();
        // xhr_want.open("POST", url_want, true);
        // xhr_want.setRequestHeader('Content-Type', 'application/json');
        // xhr_want.send(JSON.stringify(info));
        // xhr_want.onreadystatechange = function () {
        //   if (xhr_want.readyState == 4) {
        //     console.log(xhr_want.responseText)
        //     showStatus(xhr_want.responseText)
        //   }
        // }
    
        //先看看是否已经wanted过了
        if (seedId) {
            const r = await fetch(subtitlexserver + "/check_if_wanted", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    "seed_id": seedId.toString(),
                    "want_lang": wantLang
                })
            })
    
            const re = await r.text()
            //如果是,提示generating，只保存want
            if (re == "yes") {
                showStatus("generating", processStatus)
                return
            } else if (re === "fullfilled") {
                showStatus("generated")
                await checkSubTitle(tabUrl)
                return
            }
        }
    
        //如果不是，提示submitted,走want_subtitle
        const userLanguage = navigator.language || navigator.userLanguage;
        v = { "wl": wantLang + "&&" + userLanguage }
        let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        chrome.scripting.executeScript({
            args: [v],
            target: { tabId: tab.id },
            func: wantSubtitleFunc
        }).then(injectionResults => {
            let injectionResult = injectionResults[0]
            let result = injectionResult.result
            if (!result) {
                result = "submitted"
            }
            showStatus(result, seedObj?.process_status)
        });
    })
    
    document.getElementById("showSubtitle").addEventListener('click', async () => {
        console.log('showSubtitle buttun was clicked.')
        //获取到选择的language
        seedObj.video_language = document.getElementById("show_lang").value
        let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
        chrome.scripting.executeScript({
            args: [seedObj],
            target: { tabId: tab.id },
            func: showSubtitleFunc
        })
    })

    load()
   
})
function load(){
     //常量定义
    //获取激活的选项卡
    chrome.tabs.query({
        active: true,
        lastFocusedWindow: true
    }, async function (tabs) {
        let seedId
        //选取激活的选项卡
        var tab = tabs[0];
        console.log(tab.url);
        tabUrl = tab.url

        missavTheaterMode(tab.url)


        let result = await chrome.scripting.executeScript({
            target: { tabId: tab.id, allFrames: true },
            func: supportCheckFunc
        })
        console.log(result)
        const info = result[0].result
        console.log(info)
        if (!info.support) {
            showTip("Didn't find supported video stream on this page, please check the supported website list.")
            return
        }

        await checkSubTitle(tab.url)
    });
}
function missavTheaterMode(tabUrl){
        //if missav.com 
        if (tabUrl.startsWith(missav)) {
            let theaterMode = document.getElementById("theaterMode")
            theaterMode.addEventListener('click', async () => {
                let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
                chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    func: hideAds
                })
            })
            document.getElementById("theaterMode").style.display = "block";
        } else {
            document.getElementById("theaterMode").style.display = "none";
        }
}
async function checkSubTitle(tabUrl){
            //check if the page was processed
            const url = subtitlexserver + "/check_subtitle"
           
            video_no = tabUrl.split("/")[tabUrl.split("/").length - 1]
            const param = {
                pageurl: tabUrl,
                video_no: video_no
            }
            try {
                const response = await fetch(url, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        'Access-Control-Allow-Origin': '*'
                    },
                    body: JSON.stringify(param)
                })
    
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                const seed = await response.json()
                console.log(seed)
                const availLangs = []
    
                if (seed.length > 0) {            //本页已在seed列表
                    seedObj =seed[0]
                    processStatus = seed[0].process_status
                    seedId = seed[0].id
                    if (processStatus == '2' || processStatus == '3') {
                        //获取到当前seed有哪些生成过的language
                        const url1 = subtitlexserver + "/get_subtitle_info?id=" + seedId
                        const response1 = await fetch(url1, {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json"
                            }
                        })
                        const subtitles = await response1.json()
                        console.log(subtitles)
                        if (subtitles.length > 0) {
                            document.getElementById("ready").style.display = "block"
                            const show_lang = document.getElementById("show_lang")
                            show_lang.innerHTML = ''
                            for (let i = 0; i < subtitles.length; i++) {
                                var lang = subtitles[i]["language"]
                                var option = document.createElement("option")
                                option.value = lang
                                availLangs.push(lang)
                                var language = getLangNameFromLangCode(lang)
                                option.textContent = language
                                show_lang.appendChild(option)
                            }
                            let tip = "Subtitles in some languages are ready."
                            showTip(tip)
                          
                        }
                    } else { //有记录，但是没有有效字幕
                        document.getElementById("ready").style.display = "none"
                        showTip("Subtitles on this page have not been generated, pleses select the desired language and click the Want Subtitle button.")
                    }
                } else { //还没有任何记录
                    document.getElementById("ready").style.display = "none"
                    showTip("Subtitles on this page have not been generated, pleses select the desired language and click the Want Subtitle button.")
                }
    
                //添加尚未生成的语言选项
                addOptionsToWantLang(availLangs)
                //默认选择用户浏览器设置
                const userLanguage = navigator.language || navigator.userLanguage;
                //document.getElementById("want_lang").value=getWantLangFromUserLang(userLanguage)
            } catch (e) {
                console.error("Error fetching data:", e);
            }
}
function addOptionsToWantLang(availLangs) {
    tgtLangs = ["eng", "cmn", "cmn_Hant", "spa", "por", "swe", "deu", "arb", "rus", "fra", "jpn"]
    hasCount = 0
    console.log(availLangs)
    dom = document.getElementById("want_lang")
    dom.innerHTML=''
    for (var i = 0; i < tgtLangs.length; i++) {
        var langCode = tgtLangs[i]
        if (availLangs.indexOf(langCode) < 0) {
            //尚未生成
            var option = document.createElement("option")
            option.value = langCode
            option.textContent = getLangNameFromLangCode(langCode)
            dom.appendChild(option)
        } else {
            //已生成
            hasCount++
        }
    }
    //全部都已生成
    if (hasCount < tgtLangs.length) {
        document.getElementById("notyet").style.display = "block"
    }
}
function getLangNameFromLangCode(lang) {
    let language
    switch (lang) {
        case 'eng':
            language = "English"; break;
        case 'cmn_Hant':
            language = "Chinese(T)"; break;
        case 'cmn':
            language = "Chinese"; break;
        case 'spa':
            language = "Spanish"; break;
        case 'por':
            language = "Portuguese"; break;
        case 'swe':
            language = "Swedish"; break;
        case 'deu':
            language = "German"; break;
        case 'arb':
            language = "Arabic"; break;
        case 'rus':
            language = "Russian"; break;
        case 'fra':
            language = "French"; break;
        case 'jpn':
            language = "Japanese"; break;
    }
    return language
}
function getWantLangFromUserLang(userLanguage) {
    let wantLang
    if (userLanguage.startsWith("en")) {
        wantLang = "eng";
    }
    else if (userLanguage.startsWith("zh-Hant")) {
        wantLang = "cmn_Hant"
    }
    else if (userLanguage.startsWith("zh")) {
        wantLang = "cmn";
    }
    else if (userLanguage.startsWith("es")) {
        wantLang = "spa";
    }
    else if (userLanguage.startsWith("pt")) {
        wantLang = "por";
    }
    else if (userLanguage.startsWith("sv")) {
        wantLang = "swe";
    }
    else if (userLanguage.startsWith('de')) {
        wantLang = "deu";
    }
    else if (userLanguage.startsWith("ar")) {
        wantLang = "arb";
    }
    else if (userLanguage.startsWith("ru")) {
        wantLang = "rus";
    }
    else if (userLanguage.startsWith("fr")) {
        wantLang = "fra";
    }
    else if (userLanguage.startsWith("ja")) {
        wantLang = "jpn";
    }
    return wantLang
}
function showStatus(status, process_status) {
    
        let est = undefined
        if (process_status === "1" || process_status ==="1e" || process_status ==="2e" || process_status === "0" || !process_status) {
            est = " 1-2 hour "
        } else if (process_status === "2") {
            est = " 30 minutes - 1 hour "
        } else if (process_status === "3") {
            est = " several minutes "
        }

        if (est) {
            status += ", EST: " + est + "."
        }
    

    const statusDom = document.getElementById("subtitlex_status")
    statusDom.textContent = status
    setTimeout(function () {
        statusDom.textContent = " "
    }, 3000)
}
function showTip(tip) {
    document.getElementById("processing").textContent = tip
}
function hideAds() {
    try {
        document.querySelector('.plyr').parentNode.removeAttribute("@click")
        document.querySelector('.plyr').parentNode.removeAttribute("@keyup.space.window")
    } catch (e) {
        console.error(e)
    }
    try {
        const ads = document.getElementsByTagName("div")[0].children[2].children[1].children[0];
        console.log(ads);
        ads.style.display = "none";
    } catch (e) {
        console.error(e)
    }
    try {
        const ads = document.getElementsByTagName("div")[1].children[2].children[1].children[0];
        console.log(ads);
        ads.style.display = "none";
    } catch (e) {
        console.error(e)
    }

    // const popDiv = document.getElementsByClassName("plyr__controls")[0].parentNode.parentNode
    // console.log(popDiv)
    // popDiv.replaceWith(popDiv.cloneNode(true));
    // debugger
}
function wantSubtitleFunc(want_lang_value) {
    console.log(want_lang_value)
    if (document.getElementById('subtitme_want_lang_input')) {
        document.getElementById('subtitme_want_lang_input').remove()
    }
    var want_lang_input = document.createElement('input');
    want_lang_input.id = "subtitme_want_lang_input";
    want_lang_input.textContent = want_lang_value.wl;
    (document.head || document.documentElement).appendChild(want_lang_input);

    var s = document.createElement('script');
    s.src = chrome.runtime.getURL('wantsubtitle.js');
    s.onload = function () { this.remove(); };
    (document.head || document.documentElement).appendChild(s);
}
function showSubtitleFunc(seed) {

    document.getElementById("subX")?.remove()

    function dragElement(elmnt) {
        var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
        if (document.getElementById(elmnt.id + "header")) {
            // if present, the header is where you move the DIV from:
            document.getElementById(elmnt.id + "header").onmousedown = dragMouseDown;
        } else {
            // otherwise, move the DIV from anywhere inside the DIV:
            elmnt.onmousedown = dragMouseDown;
        }

        function dragMouseDown(e) {
            e = e || window.event;
            e.preventDefault();
            // get the mouse cursor position at startup:
            pos3 = e.clientX;
            pos4 = e.clientY;
            document.onmouseup = closeDragElement;
            // call a function whenever the cursor moves:
            document.onmousemove = elementDrag;
        }

        function elementDrag(e) {
            e = e || window.event;
            e.preventDefault();
            // calculate the new cursor position:
            pos1 = pos3 - e.clientX;
            pos2 = pos4 - e.clientY;
            pos3 = e.clientX;
            pos4 = e.clientY;
            // set the element's new position:
            elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
            elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
        }

        function closeDragElement() {
            // stop moving when mouse button is released:
            document.onmouseup = null;
            document.onmousemove = null;
        }
    }

    var d1 = document.createElement("div");
    d1.id = "subX"
    d1.style.position = "absolute"
    //d1.style.border = "1px solid #d3d3d3"
    d1.style.zIndex = 10000000
    d1.style.top = "600px"
    d1.style.left = "10%"
    // d1.style.width = "700px"
    d1.style.display = "flex"

    var h1 = document.createElement("div");
    h1.style.backgroundColor = "#95d6a4"
    h1.style.display = "inline-block"
    //h1.style.width = "85px"
    h1.style.height = "100px"
    h1.id = "subXheader"

    var h2 = document.createElement("div");
    h2.textContent = "subtitleX"
    h2.style.cursor = 'move'
    h2.style.display = "block"
    h2.style.height = "80px"
    h2.style.textAlign = "center"
    h2.style.lineHeight = "90px"
    h1.appendChild(h2)

    var h3 = document.createElement("div");
    h3.style.display = "block";
    h3.style.flexDirection = "row";
    h3.style.justifyContent = "space-between";
    h3.style.width = "100%";
    h3.style.height = "10px";
    var f1 = document.createElement("span");
    f1.style.cursor = "pointer"
    f1.style.backgroundColor = "yellow"
    f1.textContent = "Issue"
    h3.appendChild(f1)

    var p1 = document.createElement("span");
    p1.style.cursor = "pointer"
    p1.style.backgroundColor = "red"
    p1.textContent = "Close"
    p1.onclick = function () {
        document.getElementById("subX").remove()
    }
    h3.appendChild(p1)
    h1.appendChild(h3)

    var s3 = document.createElement('iframe');
    s3.style.width = "900px"
    s3.style.height = '100px'
    s3.style.display = "inline-block"
    //s3.style.position = "fixed"
    //s3.style.zIndex =1000
    var id = seed.id
    var language = seed.video_language
    const subtitlexserver = "https://api.subtitlex.xyz"
    s3.src = subtitlexserver + '/page/subtitle?id=' + id + '&language=' + language;
    d1.appendChild(s3)
    d1.appendChild(h1)
    document.body.appendChild(d1);
    dragElement(d1)
}
function supportCheckFunc() {
    const youtube = 'https://www.youtube.com'
    const missav = 'https://missav.com'
    const supportWebsites = [youtube, missav]
    pageUrl = window.location.href
    result = {}
    //不在支持的网站列表
    inList = false
    for (i in supportWebsites) {
        if (pageUrl.toLowerCase().startsWith(supportWebsites[i])) {
            inList = true
            break
        }
    }
    if (!inList) {
        result.support = false
        result.msg = "not in support website list."
        return result
    }
    //检查是否有有效stream
    m3u8Url = undefined
    video_no = undefined
    video_name = undefined

    if (pageUrl.toLowerCase().indexOf(youtube) >= 0) {
        if (pageUrl.toLowerCase().indexOf("watch") >= 0) {
            video_name = document.getElementsByTagName("title")[0]?.textContent;
            video_no = video_name
            m3u8Url = pageUrl
            result.support = true
        } else {
            result.msg = "youtube, not on the watch page."
            result.support = false
            return result;
        }
    } else if (pageUrl.toLowerCase().indexOf(missav) >= 0) {
        if (window.source) {
            m3u8Url = window.source
        } else if (window.source720) {
            m3u8Url = window.source720
        } else if (window.source842) {
            m3u8Url = window.source842
        } else if (window.source1280) {
            m3u8Url = window.source1280
        }
        // if (!m3u8Url) {
        //     result.msg = "missav, did't find the m3u8 url."
        //     result.support = false
        //     return result
        // }
        if (document.querySelector(".plyr__controls")) {
            result.support = true
        } else {
            result.support = false
        }
        video_no = window.location.href.split("/")[window.location.href.split("/").length - 1]
        video_name = document.getElementsByTagName("title")[0]?.textContent;
    }
    param = {
        "m3u8url": m3u8Url,
        "pageurl": pageUrl,
        "video_no": video_no,
        "video_name": video_name,
    }
    result = { ...result, ...param }
    return result

}