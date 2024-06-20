import s from './sites'

interface VideoPlayer {
  [site: string]: PlayerElement
}

export interface PlayerElement {
  video: ElementInfo,
  container: ElementInfo,
  iconWrapper: IconInfo | null,
}

interface ElementInfo {
  selector: string,
  index: number,
}

interface IconInfo extends ElementInfo {
  spacing: string,
}

const elementPosition: VideoPlayer = {
  [s.youtube]: {
    video: { selector: 'video', index: 0 },
    container: { selector: '#movie_player', index: 0 },
    iconWrapper: { selector: '.ytp-right-controls', index: 0, spacing: '0 8px' },
  },
  [s.amazon]: {
    video: { selector: 'video', index: 1 },
    container: { selector: '.scalingVideoContainer', index: 0 },
    iconWrapper: {
      selector: '.hideableTopButtons div:first-child',
      index: 0,
      spacing: '0 18px',
    },
  },
  [s.amazonATV]: {
    video: { selector: 'video', index: 0 },
    container: { selector: '.scalingVideoContainer', index: 0 },
    iconWrapper: {
      selector: '.atvwebplayersdk-hideabletopbuttons-container div:first-child',
      index: 0,
      spacing: '0 18px',
    },
  },
  [s.vimeo]: {
    video: { selector: 'video', index: 0 },
    container: { selector: '.js-player-fullscreen', index: 0 },
    iconWrapper: { selector: '.play-bar', index: 0, spacing: '0 0 0 12px' },
  },
  [s.twitch]: {
    video: { selector: 'video', index: 0 },
    container: { selector: '.video-player__container', index: 0 },
    iconWrapper: { selector: '.player-controls__right-control-group', index: 0, spacing: '0 10px' },
  },
  [s.dailymotion]: {
    video: { selector: 'video', index: 0 },
    container: { selector: '.np_Main', index: 0 },
    iconWrapper: null,
  },
  [s.tubi]: {
    video: { selector: 'video', index: 0 },
    container: { selector: '._13syz', index: 0 },
    iconWrapper: null,
  },
  [s.missav]: {
    video: { selector: 'video.player', index: 0 },
    container: { selector: '.plyr', index: 0 },
    iconWrapper:  { selector: '.plyr__menu', index: 0, spacing: '0 10px' },
  },
  [s.jable]: {
    video: { selector: 'video#player', index: 0 },
    container: { selector: '.plyr', index: 0 },
    iconWrapper:  { selector: '.plyr__menu', index: 0, spacing: '0 10px' },
  },
  [s.twitter]:{
    video: { selector: 'video', index: 0 },
    container: { selector: 'video', index: 0 },
    iconWrapper: { selector: 'div:has(> button[aria-label="Play"]) ~ div', index: 0, spacing: '0 10px' },
  },
  [s.topjav]:{
    video: { selector: 'video', index: 0 },
    container: { selector: 'video', index: 0 },
    iconWrapper: { selector: '.jw-button-container', index: 0, spacing: '0 10px' },
  },
  [s.xvideo]: {
    video: { selector: 'video', index: 0 },
    container: { selector: 'video', index: 0 },
    iconWrapper: { selector: '.buttons-bar.right', index: 0, spacing: '0 10px' },
  },
  [s.default]: {
    video: { selector: 'video', index: 0 },
    container: { selector: 'video', index: 0 },
    iconWrapper: { selector: '.plyr__menu', index: 0, spacing: '0 10px' },
  },
};

export default elementPosition;
