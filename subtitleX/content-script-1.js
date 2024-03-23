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
      console.log(m3u8Url)
      debugger
      // if (!m3u8Url) {
      //     result.msg = "missav, did't find the m3u8 url."
      //     result.support = false
      //     return result
      // }
      if(document.querySelector(".plyr__controls")){
          result.support = true
      }else {
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

supportCheckFunc() 