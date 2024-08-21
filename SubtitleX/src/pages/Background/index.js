(async () => {
  const subtitleXserverApi = 'https://api.subtitlex.xyz';
  //const subtitleXserverApi = "http://127.0.0.1:12801";
  const subtitleXserverWeb = 'https://www.subtitlex.xyz';
  const subtitlexDomain = 'www.subtitlex.xyz';

  //更新用户信息
  const updateUser = async () => {
    console.log('updateUser');
    try {
      // const storage = await chrome.storage.sync.get('user');
      // let user = storage.user;
      let user = {};
      //建立user
      if (!user) {
        console.log('[background] user not exist, create one');
        user = {};
      }
      //建立user email
      if (!user.email) {
        console.log(
          '[background] user email not exist, check user email from cookie'
        );
        const email = await checkCookie();
        user.email = email;
      }
      if (user.email) {
        //刷新user 信息，并保存进chrome.storage
        const user_info = await fetchUserInfo(user);
        Object.assign(user, user_info);
      }

      chrome.storage.sync.set({ user: user });
    } catch (e) {
      console.error(e);
    }
  };
  const fetchUserInfo = async (user) => {
    try {
      if (user.lastFetch) {
        //10s内不重复请求
        const diff =
          (new Date().getTime() - new Date(user.lastFetch).getTime()) / 1000;
        if (diff < 10) {
          console.log(
            '[fetchUserInfo] last fetch less than 10 seconds, ignore this request'
          );
          return;
        }
      }
      let url =
        subtitleXserverWeb + '/api/checkSubscription?email=' + user.email;
      console.log('[fetchUserInfo] fetch', url);
      let response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });
      let userInfo = await response.json();
      console.log('[fetchUserInfo] get user info', userInfo);
      userInfo.lastFetch = new Date().getTime();
      userInfo.subscribed = userInfo.hasSub
        ? new Date() < new Date(userInfo.expireDate * 1000)
        : false;
      return userInfo;
    } catch (e) {
      console.error('[fetchUserInfo] fetch user exception', e);
      return null;
    }
  };
  //检查www.subtitle.xyz的cookie,通过session接口获取到email，保存进storage的user对象
  const checkCookie = async () => {
    try {
      const cookies = await chrome.cookies.getAll({ domain: subtitlexDomain });
      let session_token;
      for (var i = 0; i < cookies.length; i++) {
        if (cookies[i].name === '__Secure-next-auth.session-token') {
          session_token = cookies[i].value;
        }
      }
      if (session_token) {
        console.log(
          '[checkCookie] get seesion token from cookies',
          session_token
        );
        const url = subtitleXserverWeb + '/api/auth/session';
        console.log('[checkCookie] fetch', url);
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            cookie: '__Secure-next-auth.session-token=' + session_token,
          },
        });
        const session_info = await response.json();
        console.log('[checkCookie] get seesion_info', session_info);
        const user_email = session_info?.user?.email;
        if (user_email) {
          console.log('[checkCookie] get user email', user_email);
          return user_email;
        } else {
          console.log('[checkCookie] no user email found in session');
        }
      } else {
        console.log('[checkCookie] no session token found in cookie');
      }
    } catch (e) {
      console.log(e);
    }
  };

  //开始注册事件监听
  try {
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

    //监听内部事件
    chrome.runtime.onMessage.addListener(function (request) {
      if (request.link) {
        //打开链接
        chrome.tabs.create({
          active: true,
          url: request.link,
        });
      } else if (request.action === 'updateUser') {
        //加载content.js的时候更新用户信息
        // 更新user信息
        updateUser();
      }
    });

    //extension安装更新事件
    chrome.runtime.onInstalled.addListener((details) => {
      if (details.reason === chrome.runtime.OnInstalledReason.INSTALL) {
        //首次安装，自动打开帮助页面
        chrome.tabs.create({
          url: subtitleXserverWeb + '/Extension#help',
        });
      } else if (details.reason === chrome.runtime.OnInstalledReason.UPDATE) {
        chrome.tabs.create({
          url: subtitleXserverWeb + '/Extension#help',
        });
      } else if (
        details.reason === chrome.runtime.OnInstalledReason.CHROME_UPDATE
      ) {
        // When browser is updated
      } else if (
        details.reason === chrome.runtime.OnInstalledReason.SHARED_MODULE_UPDATE
      ) {
        // When a shared module is updated
      }
    });

    //卸载事件
    chrome.runtime.setUninstallURL(
      subtitleXserverWeb + '/survey/uninstall',
      () => {}
    );

    //action点击事件
    chrome.action.onClicked.addListener(async (tab) => {
      //const prevState = await chrome.action.getBadgeText({ tabId: tab.id });
      const nextState = 'ON';
      await chrome.action.setBadgeText({
        tabId: tab.id,
        text: nextState,
      });

      //insert content script when user turns the extension on
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['contentScript.bundle.js'],
      });
    });
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
