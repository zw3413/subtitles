export const subtitleXserverApi = "https://api.subtitlex.xyz";
export const subtitleXserverWeb = "https://www.subtitlex.xyz";


export const getWantLangFromUserLang = (userLanguage) => {
  let wantLang;
  if (userLanguage.startsWith("en")) {
    wantLang = "eng";
  } else if (userLanguage.startsWith("zh-Hant") || userLanguage.startsWith("zh-TW")) {
    wantLang = "cmn_Hant";
  } else if (userLanguage.startsWith("zh")) {
    wantLang = "cmn";
  } else if (userLanguage.startsWith("es")) {
    wantLang = "spa";
  } else if (userLanguage.startsWith("pt")) {
    wantLang = "por";
  } else if (userLanguage.startsWith("sv")) {
    wantLang = "swe";
  } else if (userLanguage.startsWith("de")) {
    wantLang = "deu";
  } else if (userLanguage.startsWith("ar")) {
    wantLang = "arb";
  } else if (userLanguage.startsWith("ru")) {
    wantLang = "rus";
  } else if (userLanguage.startsWith("fr")) {
    wantLang = "fra";
  } else if (userLanguage.startsWith("ja")) {
    wantLang = "jpn";
  } else if (userLanguage.startsWith("ko")) {
    wantLang = "kor";
  } else if (userLanguage.startsWith("it")) {
    wantLang = "ita";
  } else if (userLanguage.startsWith("pl")) {
    wantLang = "pol";
  } else if (userLanguage.startsWith("tr")) {
    wantLang = "tur";
  } else if (userLanguage.startsWith("vi")) {
    wantLang = "vie";
  } else if (userLanguage.startsWith("th")) {
    wantLang = "tha";
  } else if (userLanguage.startsWith("hi")) {
    wantLang = "hin";
  } else if (userLanguage.startsWith("ms")) {
    wantLang = "msa";
  } else if (userLanguage.startsWith("id")) {
    wantLang = "ind";
  }
  return wantLang;
};
export const fetchUserInfo = async (email) => {
  console.log("fetchUserInfo")
  try {

    const storage = await chrome.storage.sync.get("user");
    const user = storage.user;

    if(user.lastFetch){
      const diff = (new Date().getTime() - new Date(user.lastFetch).getTime())/1000
      if(diff < 10){
        console.log("last fetch less than 10 seconds, ignore this request")
        return;
      }
    }

    let url = subtitleXserverWeb + "/api/checkSubscription?email=";
    let response = await fetch(url + email, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    });
    let userInfo = await response.json();
    console.log("subtitlex: user info fetched", userInfo);

    userInfo.lastFetch = new Date().getTime()
    Object.assign(user, userInfo);
    chrome.storage.sync.set({ user: user });
    console.log("subtitlex: user info saved", user);
    return userInfo;
  } catch (e) {
    console.log("subtitlex: user info fetch failed", e);
    return null;
  }

};
export const findUser = async () => {
  let storage;
  //获取用户信息
  try {
    storage = await chrome.storage.sync.get("user"); //读取user
  } catch (e) {
    console.log(e);
  }
  //如果存储中有user对象
  if (storage && storage.user) {
    //计算订阅是否有效
    storage.user.subscribed = storage.user.hasSub
      ? new Date() < new Date(storage.user.expireDate * 1000)
      : false;
    console.log("subtitlex: user info loaded", storage.user);
    //如果订阅失效，尝试更新用户信息
    if (!storage.user.subscribed && storage.user.email) {
      console.log("subtitlex: user subscription expired, try to update user info");
      let user_new = await fetchUserInfo(storage.user.email);
      if (user_new) {
        Object.assign(storage.user, user_new);
        storage.user.subscribed = user_new.hasSub
          ? new Date() < new Date(user_new.expireDate * 1000)
          : false;
        chrome.storage.sync.set({ user: storage.user });
        console.log("subtitlex: user info updated", storage.user);
      }
    }
  }
  return storage.user;
};
export const remoteCall = async (f, pl) => {
  let response;
  try {
    let user = await findUser()
    console.log("subtitlex: about to cal the remotecall with user ")
    console.log(user)
    response = await fetch(subtitleXserverApi + "/api1", {
      method: "POST",
      // headers: {
      //   "Content-Type": "application/json",
      // },
      body: JSON.stringify({
        hashcode: "xxx",
        request_id: "xxx",
        device_ip: "0.0.0.0",
        uuid: user.uuid,
        function: f,
        params: pl,
      }),
    });
    console.log("subtitlex: remoteCall response", response);
  } catch (e) {
    console.log("subtitlex: remoteCall failed", e);
    return null;
  }
  return await response.json();
};
export const fetchTextFromURL = async (subtitleId) => {
  const url = subtitleXserverApi + "/subtitle?id=" + subtitleId;
  let user = await findUser()
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "text",
      },
      body: JSON.stringify({
        hashcode: "xxx",
        request_id: "xxx",
        device_ip: "0.0.0.0",
        user: user,
      }),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
      return ''
    }
    const text = await response.text();
    return text;
  } catch (error) {
    console.log(
      " fetch subtitle failed, contact administrator." + error
    );
    return ''
  }
};
const readFile = async (file) => {
  try {
    return new Promise((resolve, reject) => {
      try {
    
        let reader = new FileReader();
        reader.onload = async () => {
          //Base64 decoding
          let result = reader.result;
          let base64 = result.split(",")[1];
          let decoding = await new Blob([base64ToArrayBuffer(base64)]).text();
          //let decoding = atob()
          resolve(decoding);
        };
        //reader.readAsText(file);
        reader.readAsDataURL(file);
      } catch (e) {
        console.log(e);
      }
    });
  } catch (e) {
    console.log(e);
  }
};
export const uploadSubtitleFile = async (seed, file) => {
  //const fileContent = await readFile(file);
  const formData = new FormData();
  formData.append("file", file);
  formData.append("filename", file.name);
  const uuid = seed.id;
  formData.append("uuid", uuid);
  fetch(subtitleXserverApi + "/api3", {
    method: "POST",
    body: formData,
  });
};