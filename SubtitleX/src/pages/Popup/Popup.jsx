import React, { useState } from 'react';
import { createTheme, ThemeProvider } from '@material-ui/core/styles';
import Header from './Header';
import SubtitleSettings from './SubtitleSettings/index';
import GeneralSection from './GeneralSection';
import Shortcuts from './Shortcuts';
import NoVideoDetected from './NoVideoDetected';
import "./index.css"
import { fontSize } from '@material-ui/system';
// For consistency across websites with different global styles
const msTheme = createTheme({
  palette: {
    primary: {
      //main: '#ba000d',
      main:'rgb(127 189 231)'
    },
    secondary: {
      //main: '#ff5722',
  
      main:'rgb(32 228 255)'
    },
  },
  overrides: {
    MuiButton: {
      root: {
        fontSize: '14px !important',
      },
      containedPrimary: {
        backgroundColor: '#ba000d !important',
      },
    },
    MuiButtonBase: {
      root: {
        color: '#000000',
      },
    },
    MuiInputBase: {
      input: {
        fontSize: '16px',
        border: 'none !important',
      },
    },
    MuiContainer: {
      root: {
        paddingLeft: '16px !important',
        paddingRight: '16px !important',
      },
    },
    MuiSvgIcon: {
      root: {
        fontSize: '24px !important',
      },
    },
    MuiTypography: {
      body1: {
        fontSize: '16px !important',
      },
    },
    MuiSwitch: {
      input: {
        position: 'absolute !important',
      },
    },
  },
});

const Popup = ({
  popup,
  setMenu,
  previouslyDetected,
  sitesWithSubtitles,
  thisSite,
}) => {
  const [displayShortcuts, setDisplayShortcuts] = useState(false);
  const [videoDetected, setVideoDetected] = useState(previouslyDetected);
  const [activating, setActivating] = useState(true);

  if (popup && activating) {
    setActivating(false);
    // Send a message to the content script to display the subtitles
    chrome.tabs.query({ currentWindow: true, active: true }, function (tab) {
      // Send a new message every 500 milliseconds until the popup closes or a video is detected
      const intervalId = setInterval(() => {
        chrome.tabs.sendMessage(
          tab[0].id,
          { activation: true },
          function (response) {
            // Display an error if no video can be detected
            console.log('popup received the response from contentscript ' + response)
            if (response && !videoDetected) {
              setVideoDetected(true);

              const thisSite = tab[0].url
                .replace(/^.*\/\//, '')
                .replace(/\/.*/, '');
 
              sitesWithSubtitles.push(thisSite);

              chrome.storage.sync.set(
                {
                  sitesWithSubtitles: sitesWithSubtitles,
                },
                function () {
                  clearInterval(intervalId);
                }
              );
            } else {
              clearInterval(intervalId);
            }
          }
        );
      }, 2000);
    });
  }

  return (
    <ThemeProvider theme={msTheme} >
      <div className='subx-w-[280px]' style={{fontSize:"16px"}}>
      {displayShortcuts ? (
        <Shortcuts
          setDisplayShortcuts={setDisplayShortcuts}
          thisSite={thisSite}
        />
      ) : (
        <>
          {/* <Header popup={popup} /> */}
          {popup && !videoDetected ? (
            <NoVideoDetected />
          ) : (
            <SubtitleSettings  popup={popup} setMenu={setMenu} />
          )}
          <GeneralSection
            setDisplayShortcuts={setDisplayShortcuts}
            popup={popup}
          />
        </>
      )}</div>
    </ThemeProvider>
  );
};

export default Popup;
