export const subtitleXserverApi = 'https://api.subtitlex.xyz';
//export const subtitleXserverApi = "http://127.0.0.1:12801";
export const subtitleXserverWeb = 'https://www.subtitlex.xyz';

export const getWantLangFromUserLang = (userLanguage) => {
  let wantLang;
  if (userLanguage.startsWith('en')) {
    wantLang = 'eng';
  } else if (
    userLanguage.startsWith('zh-Hant') ||
    userLanguage.startsWith('zh-TW')
  ) {
    wantLang = 'cmn_Hant';
  } else if (userLanguage.startsWith('zh')) {
    wantLang = 'cmn';
  } else if (userLanguage.startsWith('es')) {
    wantLang = 'spa';
  } else if (userLanguage.startsWith('pt')) {
    wantLang = 'por';
  } else if (userLanguage.startsWith('sv')) {
    wantLang = 'swe';
  } else if (userLanguage.startsWith('de')) {
    wantLang = 'deu';
  } else if (userLanguage.startsWith('ar')) {
    wantLang = 'arb';
  } else if (userLanguage.startsWith('ru')) {
    wantLang = 'rus';
  } else if (userLanguage.startsWith('fr')) {
    wantLang = 'fra';
  } else if (userLanguage.startsWith('ja')) {
    wantLang = 'jpn';
  } else if (userLanguage.startsWith('ko')) {
    wantLang = 'kor';
  } else if (userLanguage.startsWith('it')) {
    wantLang = 'ita';
  } else if (userLanguage.startsWith('pl')) {
    wantLang = 'pol';
  } else if (userLanguage.startsWith('tr')) {
    wantLang = 'tur';
  } else if (userLanguage.startsWith('vi')) {
    wantLang = 'vie';
  } else if (userLanguage.startsWith('th')) {
    wantLang = 'tha';
  } else if (userLanguage.startsWith('hi')) {
    wantLang = 'hin';
  } else if (userLanguage.startsWith('ms')) {
    wantLang = 'msa';
  } else if (userLanguage.startsWith('id')) {
    wantLang = 'ind';
  }
  return wantLang;
};

export const findUser = async () => {
  try {
    const storage = await chrome.storage.sync.get('user'); 
    if (storage && storage.user) {
      return storage.user;
    }else{
      console.error("[common findUser] can't find user from storage")
    }
  } catch (e) {
    console.error("[common findUser] find user from strorage exception",e);
  }
};
export const remoteCall = async (f, pl) => {
  let response;
  try {
    // let user = await findUser()
    //  console.log("subtitlex: about to cal the remotecall with user ")
    // console.log(user)
    response = await fetch(subtitleXserverApi + '/api1', {
      method: 'POST',
      // headers: {
      //   "Content-Type": "application/json",
      // },
      body: JSON.stringify({
        hashcode: 'xxx',
        request_id: 'xxx',
        device_ip: '0.0.0.0',
        //    user: user,
        function: f,
        params: pl,
      }),
    });
  } catch (e) {
    console.error('[remoteCall] exception', e);
    return null;
  }
  return await response.json();
};
export const fetchTextFromURL = async (subtitleId, mode, user) => {
  const url = subtitleXserverApi + '/subtitle?id=' + subtitleId +"&mode="+mode;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'text',
      },
      body: JSON.stringify({
        hashcode: 'xxx',
        request_id: 'xxx',
        device_ip: '0.0.0.0',
        user: user,
      }),
    });
    return response;
  } catch (error) {
    console.log('[common] fetchTextFromURL exception' + error);
    return null;
  }
};
function base64ToArrayBuffer(base64) {
  var binary_string = window.atob(base64);
  var len = binary_string.length;
  var bytes = new Uint8Array(len);
  for (var i = 0; i < len; i++) {
    bytes[i] = binary_string.charCodeAt(i);
  }
  return bytes.buffer;
}
const readFile = async (file) => {
  try {
    return new Promise((resolve, reject) => {
      try {
        let reader = new FileReader();
        reader.onload = async () => {
          //Base64 decoding
          let result = reader.result;
          let base64 = result.split(',')[1];
          // eslint-disable-next-line no-undef
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
  formData.append('file', file);
  formData.append('filename', file.name);
  const uuid = seed.id;
  formData.append('uuid', uuid);
  fetch(subtitleXserverApi + '/api3', {
    method: 'POST',
    body: formData,
  });
};
