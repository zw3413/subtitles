import React, { useEffect } from 'react';
import { render } from 'react-dom';
import Content from './Content';
import videoPlayerDetector from './videoPlayerDetector/videoPlayerDetector';

if (!document.querySelector('#subtitlex_injectScript')) {
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
//document.addEventListener('DOMContentLoaded', () => {
window.addEventListener('load', () => {
  if (!displayingExtension) {
    console.log('start to detect the video player');
    // Try to detect the video and display the subtitles
    const video = videoPlayerDetector('video');
    const container = videoPlayerDetector('container');
    const iconWrapper = videoPlayerDetector('iconWrapper');

    if (video && container) {
      //检测missav.com和jable.tv的seed
      window.postMessage({
        from: 'subtitlex_contentScript',
        type: 'detectSeed',
        data: {},
      });
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
        const thisSite = tab.url.replace(/^.*\/\//, '').replace(/\/.*/, '');
        sitesWithSubtitles.push(thisSite);
        chrome.storage.sync.set({
          sitesWithSubtitles: sitesWithSubtitles,
        });
      });
    }
  }
});
