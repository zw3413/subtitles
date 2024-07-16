import React from 'react';
import { render } from 'react-dom';

export default function detectSeed() {
  let jh_seed = null;

  //jable.tv
  if (typeof hlsUrl != 'undefined' && typeof jh_currentUrl == 'undefined') {
    let jh_currentUrl = top.location?.href;

    jh_seed = {
      videoNo: jh_currentUrl.split('/')[jh_currentUrl.split('/').length - 2],
      videoName: document.querySelector('.video-info .info-header h4')
        .textContent,
      m3u8Url: hlsUrl,
      pageUrl: jh_currentUrl,
    };
  }
  //missav.com
  if (typeof source1280 != 'undefined' && typeof jh_currentUrl == 'undefined') {
    let jh_currentUrl = window.location.href;
    jh_seed = {
      videoNo: jh_currentUrl.split('/')[jh_currentUrl.split('/').length - 1],
      videoName: document.querySelector('title').textContent,
      m3u8Url: source1280,
      pageUrl: jh_currentUrl,
    };
  }

  if (
    document.querySelector('video')?.getAttribute('data-poster')?.split('/')
      .length >= 8
  ) {
    jh_seed = {
      videoNo: document
        .querySelector('video')
        .getAttribute('data-poster')
        .split('/')[
        document.querySelector('video').getAttribute('data-poster').split('/')
          .length - 2
      ],
      videoName: '',
      m3u8Url: '',
      pageUrl: window.location.href,
    };
  }

  if (!jh_seed) {
    //检测其他网址，构建seed
    jh_seed = {
      videoNo: '',
      videoName: document.title,
      pageUrl: window.location.href,
      m3u8Url: '',
    };
  }

  if (jh_seed) {
    window.postMessage({
      seed: jh_seed,
      from: 'subtitlex_injectScript',
      type: 'seed_detected',
    });
  }
}

window.addEventListener('message', async (event) => {
  if (
    event.data.from === 'subtitlex_contentScript' &&
    event.data.type === 'detectSeed'
  ) {
    detectSeed();
  }
});
