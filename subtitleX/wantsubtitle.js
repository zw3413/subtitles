
function wantSubtitleFunc() {
  const subtitlexServer = "https://api.subtitlex.xyz"
  try {

    m3u8Url = undefined
    pageUrl = window.location.href
    video_no = "subtitleX"
    video_name = document.getElementsByTagName("title")[0].textContent;
    want_lang = document.getElementById("subtitme_want_lang_input").textContent;

    if (pageUrl.toLowerCase().indexOf("youtube.com") >= 0) {
      m3u8Url = pageUrl;
      video_no = document.getElementsByTagName("title")[0].textContent;
    } else {
      if (window.source) {
        m3u8Url = window.source
      } else if (window.source720) {
        m3u8Url = window.source720
      } else if (window.source842) {
        m3u8Url = window.source842
      } else if (window.source1280) {
        m3u8Url = window.source1280
      }
      video_no = window.location.href.split("/")[window.location.href.split("/").length - 1]
    }

    if (m3u8Url) {
      param = {
        "m3u8url": m3u8Url,
        "pageurl": pageUrl,
        "video_no": video_no,
        "video_name": video_name,
        "want_language" : want_lang
      }
      let url_want = subtitlexServer+"/want_subtitle"
      let xhr_want = new XMLHttpRequest();
      xhr_want.open("POST", url_want, true);
      //xhr_want.setRequestHeader('Access-Control-Allow-Headers', '*');
      xhr_want.setRequestHeader('Content-Type', 'application/json');
      xhr_want.send(JSON.stringify(param));
      xhr_want.onreadystatechange = async function () {
        if (xhr_want.readyState == 4) {
          result = xhr_want.responseText
          console.log(result);
          //const response = await chrome.tabs.sendMessage(tab.id, { result: result });
          // do something with response here, not outside the function
          //console.log(response);
        }
      }
    }

  } catch (e) {
    console.error(e)
  }
}

wantSubtitleFunc()