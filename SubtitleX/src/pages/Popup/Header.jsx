import React from 'react';
import { styled } from '@mui/material/styles';
import openPage from './openPage';

const Title = styled('h1')({
  color: 'black !important',
  marginTop: '20px !important',
  textAlign: 'center !important',
  fontSize: '24px !important',
  fontWeight: '400 !important',
});

const Icon = styled('img')({
  display: 'block !important',
  margin: '5px auto 20px auto !important',
  cursor: 'pointer',
});

const Header = ({ popup }) => {
  return (
    <>
      {/* <Title>SubtitleX</Title> */}
      {/* <Icon
        src={chrome.runtime.getURL('/subtitlex-128.png')}
        alt="SubtitleX"
        onClick={() =>
          openPage(
            popup,
            'https://github.com/gignupg/Movie-Subtitles-Chrome-Extension'
          )
        }
      ></Icon> */}
    </>
  );
};

export default Header;
