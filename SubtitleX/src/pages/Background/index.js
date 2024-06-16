(async () => {
  const subtitleXserverApi = 'https://api.subtitlex.xyz';
  const subtitleXserverWeb = 'https://www.subtitlex.xyz';
  const subtitlexDomain = 'www.subtitlex.xyz';
  const checkCookie = async () => {
    try {
      const cookies = await chrome.cookies.getAll({ domain: subtitlexDomain });

      let session_token;
      for (var i = 0; i < cookies.length; i++) {
        if (cookies[i].name == '__Secure-next-auth.session-token') {
          session_token = cookies[i].value;
        }
      }
      console.log('get seesion token :' + session_token);

      const response = await fetch(subtitleXserverWeb + '/api/auth/session', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          cookie: '__Secure-next-auth.session-token=' + session_token,
        },
      });
      const session_info = await response.json();
      console.log(session_info);
      const user_email = session_info?.user?.email;
      if (user_email) {
        console.log('get user email :' + user_email);
        const storage = await chrome.storage.sync.get('user');
        const user = storage.user;
        user.email = user_email;
        chrome.storage.sync.set({ user: user });
      }
    } catch (e) {
      console.log(e);
    }
  };
  const UUID = async () => {
    try {
      const response = await fetch(subtitleXserverApi + '/api2', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      console.log(response);
      if (response.status == '200') {
        const result = await response.json();
        if (result.rc == '000') {
          return result.data;
        }
      }
      return 'xxxx';
    } catch (e) {
      console.log(e);
    }
  };
  try {
    const uuid = await UUID();
    chrome.storage.sync.set({ user: { uuid: uuid } });
    await checkCookie();
    //监听外部消息，接受来自subtitlex.xyz的登陆用户，并保存
    chrome.runtime.onMessageExternal.addListener(
      async (obj, sender, response) => {
        const { from, type, data } = obj;
        if (from === 'jh_web' && type === 'sendToken') {
          const storage = await chrome.storage.sync.get('user');
          const user = storage.user;
          Object.assign(user, data.user);
          chrome.storage.sync.set({ user: user });
        }
        response({ success: 'received' });
      }
    );
    chrome.runtime.onMessage.addListener(function (request) {
      if (request.link) {
        chrome.tabs.create({
          active: true,
          url: request.link,
        });
      } else if (request.action === 'checkCookie') {
        checkCookie();
      }
    });
    chrome.runtime.onInstalled.addListener((details) => {
      if (details.reason === chrome.runtime.OnInstalledReason.INSTALL) {
        // Code to be executed on first install
        // eg. open a tab with a url
        chrome.tabs.create({
          url: subtitleXserverWeb + '/Extension#help',
        });
      } else if (details.reason === chrome.runtime.OnInstalledReason.UPDATE) {
        // When extension is updated
      } else if (details.reason === chrome.runtime.OnInstalledReason.CHROME_UPDATE) {
        // When browser is updated
      } else if (details.reason === chrome.runtime.OnInstalledReason.SHARED_MODULE_UPDATE) {
        // When a shared module is updated
      }
    });
    chrome.runtime.setUninstallURL(
      subtitleXserverWeb + '/survey/uninstall',
      () => {}
    );
  } catch (e) {
    console.log(e);
  }
})();

// chrome.runtime.onInstalled.addListener(()=>{
//   chrome.action.setBadgeText({
//     text:'ON'
//   })
// })

// chrome.action.onClicked.addListener(async (tab)=>{
//   const prevState = await chrome.action.getBadgeText({tabId: tab.id});
//   const nextState = prevState == 'ON'?'OFF':'ON';
//   await chrome.action.setBadgeText({
//     tabId: tab.id,
//     text:nextState
//   })
//   const tabs = await chrome.tabs.query({
//     currentWindow: true,
//     active: true,
//   });
//   if (nextState == 'ON'){
//     activeContentScript(tab[0].id)
//   }
// })

//激活content-script
// const activeContentScript = (tabId, tab) => {
//   try {
//     chrome.tabs.sendMessage(tabId, { activation: true }, function () {
//       if (chrome.runtime.lastError) {
//         console.log(chrome.runtime.lastError.message);
//     } else {
//       //if (typeof response !== 'undefined' && response) {
//       chrome.storage.sync.get('sitesWithSubtitles', function (storage) {
//         let sitesWithSubtitles = [];
//         if (storage.sitesWithSubtitles) {
//           sitesWithSubtitles = storage.sitesWithSubtitles;
//         }
//         const thisSite = tab.url.replace(/^.*\/\//, '').replace(/\/.*/, '');
//         sitesWithSubtitles.push(thisSite);
//         chrome.storage.sync.set({
//           sitesWithSubtitles: sitesWithSubtitles,
//         });
//       });
//     }

//       //chrome.action.setIcon({path:"subtitlex-32-active.png"},()=>{})
//       //}
//     });
//   } catch (e) {
//     console.log(e);
//   }
// };

//监听chrome的tab update事件
// try {
//   chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
//     console.log('--------------');
//     console.log(changeInfo?.status);
//     console.log(changeInfo);
//     console.log(tab);
//     if (changeInfo?.status && changeInfo.status === 'complete') {
//       if (tab.url.indexOf('http') < 0) {
//         return;
//       }
//       //console.log(tab.url)
//       // const currentState = await chrome.action.getBadgeText({tabId: tabId});
//       // const currentState = 'ON';
//       // if (currentState != 'ON') {
//       //   return;
//       // }
//       try {
//        // setTimeout(() => {
//           activeContentScript(tabId, tab);
//        // }, 2000);
//       } catch (e) {
//         console.log(e);
//       }
//     }
//   });
// } catch (e) {
//   console.log(e);
// }
