import React, { useEffect, useState, useRef } from 'react';
import Container from '@mui/material/Container';
import makeStyles from '@mui/styles/makeStyles';
import FormControl from '@mui/material/FormControl';

import {
  getWantLangFromUserLang,
  remoteCall,
  fetchTextFromURL,
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

const SubtitleX = ({hide, setHide, setMenu}) => {
  const defaultSubtitleId = "0"
  const defaultChooseASubtitle = 'Choose a subtitle'
  const NoneSubtitleCollected = 'None subtitle collected'
  const classes = useStyles();
  //const [seed, setSeed] = useState({})
  const [subtitleId, setSubtitleId] = useState(defaultSubtitleId);
  const [subtitleArray, setSubtitleArray] = useState([]);
  const [listening, setListening] = useState(false);
  const [chooseASubtitle, setChooseASubtitle] = useState(defaultChooseASubtitle)

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
    if (result && result.rc === '000') {
      seed = JSON.parse(result.data);
      return seed;
    } else {
      return null;
    }
  };
  const showSubtittle = async () => {
    console.log('subtitlex: showSubtitle ' + subtitleId);
    //从server获取到文件
    if (subtitleId && subtitleId.length > 0) {
      const sub_text = await fetchTextFromURL(subtitleId);
      const sub_blob = new Blob([sub_text], { type: 'text/plain' });
      const sub_file = new File([sub_blob], 'subtitle.srt', {
        type: 'text/plain',
      });
      const eventFileUpload = new CustomEvent('fileUpload', {
        detail: sub_file,
      });
      document.dispatchEvent(eventFileUpload);
      setHide(false);
    }
  };
  if (!listening) {
    setListening(true);
    //listen to the message of seed_detected
    window.addEventListener('message', async (event) => {
      console.log('subx subtitlex  received message ');
      if (
        event.source === window &&
        event.data.from === 'subtitlex_injectScript' &&
        event.data.type === 'seed_detected'
      ) {
        console.log('subx subtitlex  received seed_detected message ');
        console.log(event.data)
        const pageUrl = event.data.seed.pageUrl;
        const s = await saveAndCheckStatusOfSeed(event.data.seed); //到后端获取seed信息
        if (s) {
          s.url = pageUrl;
          //显示subtitlex字幕信息
          console.log('subtitlex: detected seed:');
          console.log(s);
          //setSeed(s)
          seed = s;
          if (s && s.subtitle) {
            setSubtitleArray(s.subtitle);
          }
          //用户选择字幕事件
        }
      }
    });
  }
  useEffect(() => {
    if (subtitleArray && subtitleArray.length > 0) {
      setChooseASubtitle(defaultChooseASubtitle)
      //自动选择用户浏览器语言
      const userLanguage = navigator.language || navigator.userLanguage;
      const userLangCode = getWantLangFromUserLang(userLanguage);
      console.log(subtitleArray);
      console.log('subtitlex: userLanguage = ' + userLangCode);

      for (var i = 0; i < subtitleArray.length; i++) {
        if (subtitleArray[i]['language'] == userLangCode) {
          setSubtitleId(subtitleArray[i]['uuid']);
          break;
        }
      }
    }else{
      setChooseASubtitle(NoneSubtitleCollected)
    }
  }, [subtitleArray]);
  useEffect(() => {
    if (subtitleId && subtitleId !== defaultSubtitleId) {
      console.log('subtitlex: subtitleId changed');
      console.log(subtitleId);
      showSubtittle();
      setMenu(false);
    }
  }, [subtitleId]);
  const [age, setAge] = React.useState('');
  const handleChange = (event) => {
    setAge(event.target.value);
  };
  return (
    <Container className="subx-my-4">
      <FormControl variant="outlined" className={classes.formControl}>
        {/* <label
          for="subtitlex-language-select"
          className=" subx-block subx-mb-2 subx-text-[16px] subx-font-medium subx-text-gray-900 "
        >
          SubtitleX
        </label> */}
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
      </FormControl>
    </Container>
  );
};

export default SubtitleX;
