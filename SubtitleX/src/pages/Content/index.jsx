import React, { useEffect } from 'react';
import { render } from 'react-dom';
import Content from './Content';
import videoPlayerDetector from './videoPlayerDetector/videoPlayerDetector';

//注入js，获取原window下的变量
if (!document.querySelector('#subtitlex_injectScript')) {
  console.log('[content] inject script injected ');
  var s = document.createElement('script');
  s.src = chrome.runtime.getURL('injectScript.bundle.js');
  s.id = 'subtitlex_injectScript';
  (document.head || document.documentElement).appendChild(s);
}

// Wait for the popup message
// chrome.runtime.onMessage.addListener(function (msg, sender, sendResponse) {
//   if (msg.activation) {
//     if (!displayingExtension) {
//       // Try to detect the video and display the subtitles
//       const video = videoPlayerDetector('video');
//       const container = videoPlayerDetector('container');
//       const iconWrapper = videoPlayerDetector('iconWrapper');

//       if (video && container) {
//         //检测missav.com和jable.tv的seed
//         window.postMessage({
//           from: 'subtitlex_contentScript',
//           type: 'detectSeed',
//           data: {},
//         });
//         // Video detected
//         sendResponse();
//         // Render the subtitles and the menu
//         render(<Content video={video} iconWrapper={iconWrapper} />, container);
//         // Make sure only to inject the extension code once!
//         displayingExtension = true;
//       } else {
//         sendResponse();
//       }
//     } else if (displayingExtension) {
//       // The video has already been detected and the subtitles are already being displayed
//       sendResponse();
//     }
//   }
// });
let displayingExtension = false;
let detectTime = 0;
const detectAndShowSubtitles = () => {
  if (!displayingExtension) {
    detectTime++;
    console.log('[content] start to detect the video player');
    // Try to detect the video and display the subtitles
    const video = videoPlayerDetector('video');
    const container = videoPlayerDetector('container');
    const iconWrapper = videoPlayerDetector('iconWrapper');

    if (!video) {
      console.log('[content] video was not detected');
    }
    if (!container) {
      console.log('[content] container was not detected');
    }
    if (!iconWrapper) {
      console.log('[content] iconWrapper was not detected');
    }

    if (video && container && iconWrapper) {
      // Video detected
      // Render the subtitles and the menu
      render(<Content video={video} iconWrapper={iconWrapper} />, container);
      // Make sure only to inject the extension code once!
      displayingExtension = true;
      chrome.storage.sync.get('sitesWithSubtitles', function (storage) {
        let sitesWithSubtitles = [];
        if (storage.sitesWithSubtitles) {
          sitesWithSubtitles = storage.sitesWithSubtitles;
        }
        const thisSite = window.location.href
          .replace(/^.*\/\//, '')
          .replace(/\/.*/, '');
        if (!sitesWithSubtitles.includes(thisSite)) {
          sitesWithSubtitles.push(thisSite);
          chrome.storage.sync.set({
            sitesWithSubtitles: sitesWithSubtitles,
          });
        }
      });
    } else {
      if (detectTime < 5) {
        setTimeout(detectAndShowSubtitles, 5000);
      }
    }
  }
};

if (document.readyState === 'complete') {
  console.log('[content] document is ready, subtitlex will start now.');
  detectAndShowSubtitles();
} else {
  console.log(
    '[content] document is not ready, subtitlex will be started after the window loaded'
  );
  window.addEventListener('load', detectAndShowSubtitles);
}
