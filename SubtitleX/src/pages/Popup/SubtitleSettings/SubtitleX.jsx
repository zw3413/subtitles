import React, { useEffect, useState, useRef } from 'react';
import Container from '@mui/material/Container';
import makeStyles from '@mui/styles/makeStyles';
import FormControl from '@mui/material/FormControl';
import { Link } from '@mui/material';
import {
  getWantLangFromUserLang,
  remoteCall,
  fetchTextFromURL,
  findUser,
} from '../Common.jsx';

const useStyles = makeStyles((theme) => ({
  formControl: {
    minWidth: 120,
    fontSize: '16px',
    width: '100%',
  },
  selectEmpty: {
    marginTop: theme.spacing(2),
  },
  menuItem: {
    fontSize: '16px',
  },
}));

let seed = null;

export function getSeed() {
  return seed;
}

const SubtitleX = ({ hide, setHide, setMenu }) => {
  const defaultSubtitleId = '0';

  const classes = useStyles();
  //const [seed, setSeed] = useState({})
  const [subtitleId, setSubtitleId] = useState(defaultSubtitleId);
  const [subtitleArray, setSubtitleArray] = useState([]);
  const [listening, setListening] = useState(false);
  const [chooseASubtitle, setChooseASubtitle] = useState(
    chrome.i18n.getMessage('chooseSubtitle')
  );
  const [subtitle, setSubtitle] = useState('');
  const tip = 'Subscribe to www.subtitlex.xyz/Member please';
  const handleSelectChange = (event) => {
    setSubtitleId(event.target.value);
  };
  const saveAndCheckStatusOfSeed = async (seed) => {
    const params = [
      seed.videoNo,
      seed.videoName,
      seed.m3u8Url,
      seed.pageUrl,
      seed.desc,
      seed.client,
    ];
    const result = await remoteCall(
      '02ff8823-a0fd-420b-b39e-53b3a488365a',
      params
    );
    if (
      result &&
      result.rc === '000' &&
      result.data &&
      result.data.length > 0
    ) {
      seed = JSON.parse(result.data);
      return seed;
    } else {
      return null;
    }
  };
  const showSubtittle = async () => {
    console.log('[subtitlex] showSubtitle ' + subtitleId);
    //从server获取到文件
    if (subtitleId && subtitleId.length > 0) {
      let user = await findUser();
      let mode = 'demo';
      if (user && user.hasSub && user.user_secret) {
        mode = 'full';
      }
      console.log('[subtitlex] with user:', user, 'mode:', mode);
      const response = await fetchTextFromURL(subtitleId, mode, user);
      console.log('[subtitlex] response ', response);
      if (response.status !== 200) {
        const msg = await response.text();
        console.error('[subtitlex] fetch subtitle error ', msg);
        //提示报错信息
      }
      const sub_text = await response.text();
      if (!sub_text || sub_text.length === 0) {
        console.error('[subtitlex] fetch subtitle empty ');
        return;
      }
      //添加提示注册的字幕
      setSubtitle(sub_text);
      const sub_blob = new Blob([sub_text], { type: 'text/plain' });
      const sub_file = new File([sub_blob], 'subtitle.srt', {
        type: 'text/plain',
      });
      const eventFileUpload = new CustomEvent('fileUpload', {
        detail: {
          file: sub_file,
          mode:mode
        }      });
      console.log('[subtitlex] dispatchEvent fileUpload ', eventFileUpload);
      document.dispatchEvent(eventFileUpload);
      setHide(false);
    }
  };
  const subtitleArrayLoadedHandler = async () => {
    if (subtitleArray && subtitleArray.length > 0) {
      setChooseASubtitle(chrome.i18n.getMessage('chooseSubtitle'));
      //自动选择用户浏览器语言
      const userLanguage = navigator.language || navigator.userLanguage;
      const userLangCode = getWantLangFromUserLang(userLanguage);
      console.log(
        '[subtitlex] try to load subtitle in userLanguage ',
        userLangCode
      );

      for (var i = 0; i < subtitleArray.length; i++) {
        if (
          subtitleArray[i]['language'] == userLangCode ||
          subtitleArray[i]['language'] == userLangCode + '_Hant'
        ) {
          console.log(
            '[subtitlex] find subtitle in userLanguage ',
            subtitleArray[i]
          );
          setSubtitleId(subtitleArray[i]['uuid']);
          break;
        }
      }
    } else {
      setChooseASubtitle(chrome.i18n.getMessage('noneSubtitle'));
    }
  };
  if (!listening) {
    //listen to the message of seed_detected
    window.addEventListener('message', async (event) => {
      if (
        event.source === window &&
        event.data.from === 'subtitlex_injectScript' &&
        event.data.type === 'seed_detected'
      ) {
        console.log(
          '[subtitlex]  received seed_detected message with obj ',
          event.data
        );
        const pageUrl = event.data.seed.pageUrl;
        const s = await saveAndCheckStatusOfSeed(event.data.seed); //到后端获取seed信息
        if (s) {
          s.url = pageUrl;
          //显示subtitlex字幕信息
          console.log('[subtitlex] detected seed:', s);
          //setSeed(s)
          seed = s;
          if (s && s.subtitle) {
            setSubtitleArray(s.subtitle);
          }
          console.log('[subtitlex] subtitle list is ready ', s.subtitle);
        }
      }
    });
    //检测missav.com和jable.tv的seed
    setTimeout(() => {
      window.postMessage({
        from: 'subtitlex_contentScript',
        type: 'detectSeed',
        data: {},
      });
      console.log('[subtitlex] send message detectSeed');
    }, 3000);
    setListening(true);
  }
  useEffect(() => {
    subtitleArrayLoadedHandler();
  }, [subtitleArray]);

  //改变subtitleId
  useEffect(() => {
    if (subtitleId && subtitleId !== defaultSubtitleId) {
      console.log('[subtitlex] selected subtitleId changed ', subtitleId);
      showSubtittle();
      setMenu(false);
    }
  }, [subtitleId]);

  return (
    <Container className="subx-my-4 subx-mt-8">
      <FormControl variant="outlined" className={classes.formControl}>
        <div>
          {subtitle.includes(tip) ? (
            <div className=" text-red-400 subx-leading-tight">
              <a
                href="https://www.subtitlex.xyz/Member"
                target="_blank"
                rel="noopener noreferrer"
                className="subx-underline subx-text-[#20e4ff] "
              >
                {chrome.i18n.getMessage('reachLimit')}
              </a>
            </div>
          ) : (
            <></>
          )}
        </div>
        <select
          value={subtitleId}
          onChange={handleSelectChange}
          id="subtitlex-language-select"
          className="subx-bg-gray-50 subx-border subx-text-[16px] subx-border-gray-300 subx-text-gray-900 subx-rounded-lg focus:subx-ring-blue-500 focus:subx-border-blue-500 subx-block subx-w-full subx-p-2.5 "
        >
          <option value={defaultSubtitleId}>{chooseASubtitle}</option>

          {subtitleArray.map((sub, index) => {
            return (
              <option key={index} value={sub['uuid']}>
                {' '}
                {sub['language'] + '-' + sub['subtitle_name']}
              </option>
            );
          })}
        </select>
        <Link
          href="http://www.subtitlex.xyz"
          style={{ fontSize: '12px', textAlign: 'right', marginTop: '6px' }}
          target="_blank"
        >
          {chrome.i18n.getMessage('checkSubtitlexLibrary')}
        </Link>
      </FormControl>
    </Container>
  );
};

export default SubtitleX;
