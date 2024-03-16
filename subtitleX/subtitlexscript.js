


function getSubtitleFunc(id) {

    let url_get = "http://localhost:12801/get_subtitle"
    let xhr_get = new XMLHttpRequest();
    xhr_get.open("POST", url_get, true);
    xhr_get.setRequestHeader('Content-Type', 'application/json');
    param = {
      "id": id,
      "language": "en",
    }
    xhr_get.send(JSON.stringify(param));
    xhr_get.onreadystatechange = function () {
      if (xhr_get.readyState == 4) {
        result = eval(xhr_get.responseText)
        console.log(result);
        //show the subtitleX 
        
      }
    }
  }
  
  
  function wantSubtitleFunc() {
    try {
      //request the url resource via http protocol
  
      let url_want = "http://localhost:12801/want_subtitle"
      let xhr_want = new XMLHttpRequest();
      xhr_want.open("POST", url_want, true);
  
      //xhr_want.setRequestHeader('Access-Control-Allow-Headers', '*');
      xhr_want.setRequestHeader('Content-Type', 'application/json');
  
      m3u8Url = undefined
  
      pageUrl = window.location.href
      video_no = "subtitleX"
      video_name = document.getElementsByTagName("title")[0].textContent;
  
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
          "video_name": video_name
        }
        xhr_want.send(JSON.stringify(param));
        xhr_want.onreadystatechange = function () {
          if (xhr_want.readyState == 4) {
            result = eval(xhr_want.responseText)
            console.log(result);
            if (result.length > 0) {
              seed = result[0]
            }
  
            if (seed.process_status == '2') {
              getSubtitleFunc(seed.id.toString())
            }
          }
        }
      }
  
    } catch (e) {
      console.error(e)
    }
  }
  
  //wantSubtitleFunc()
if(typeof xpanel === "undefined"){
    const xpanel = document.createElement("div");
    xpanel.className = 'xPanel_out'
    const wantXButton = document.createElement("button");
    wantXButton.textContent = "Want Subtitle";
    wantXButton.onclick = function(){ 
      wantSubtitleFunc()
    }
    xpanel.appendChild(wantXButton)
    document.querySelector('body').insertAdjacentElement("beforeend", xpanel)


    const showXButton = document.createElement("button");
    showXButton.textContent="Show Subtitle";
    showXButton.onclick = function(){
      showSubtitleFunc()
    }
    xpanel.appendChild(showXButton)

}

function showSubtitleFunc(){

  const x = document.createElement("iframe");
  x.src = "http://"

  //document.querySelector('body').insertAdjacentElement("beforeend", x)
}