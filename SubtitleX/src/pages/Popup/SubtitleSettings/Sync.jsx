import React, { useState } from 'react';
import FormControl from '@material-ui/core/FormControl';
import FormGroup from '@material-ui/core/FormGroup';
import Switch from '@material-ui/core/Switch';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import MenuHeading from '../MenuHeading';
import Container from '@material-ui/core/Container';
import Slider from '@material-ui/core/Slider';
import Input from '@material-ui/core/Input';
import { makeStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import SyncIcon from '@material-ui/icons/Sync';
import Box from '@material-ui/core/Box';


const Sync = ({ popup }) => {

  const [direction, setDirection] = useState(false);
  const [syncValue, setSyncValue] = useState(0);
  const [listening, setListening] = useState(false);

  const handleInputChange = (event) => {
    setSyncValue(event.target.value === '' ? '' : Number(event.target.value));

    if(syncValue < 0){
      setSyncValue(syncValue * -1)
      setDirection(true)
    }else{
      setDirection(false)
    }

    handleSync({ syncValue: syncValue, syncLater: direction })
  };

  // const handleBlur = () => {
  //   if (syncValue < 0) {
  //     setSyncValue(0);
  //   } else if (syncValue > 10) {
  //     setSyncValue(10);
  //   }
  // };

  function handleSync(synchronization) {
    if (popup) {
      chrome.tabs.query({ currentWindow: true, active: true }, function (tab) {
        chrome.tabs.sendMessage(tab[0].id, synchronization);
      });
    } else {
      // Dispatch message to the subtitle component
      const syncNow = new CustomEvent('syncNow', {
        detail: synchronization,
      });
      document.dispatchEvent(syncNow);
    }
  }

  if (!popup && !listening) {
    setListening(true);
    chrome.runtime.onMessage.addListener((msg) => {
      if (msg.syncValue) {
        // This time calling handleSync from the content script instead of from the popup
        handleSync(msg);
      }
    });
  }

  return (
    <>
      {/* <MenuHeading heading="Synchronization:" /> */}
      <Container>

        <Box my={3} className='subx-flex subx-justify-between'>
          <Input
            className='inline'
            color="primary"
            value={syncValue}
            margin="dense"
            onChange={handleInputChange}
            onBlur={handleBlur}
            inputProps={{
              step: 1,
              min: -15,
              max: 15,
              type: 'number'
            }}
          />
          <h1 className='subx-inline subx-font-sans subx-text-base subx-text-yellow-700'>seconds</h1>

        </Box>
      </Container>
    </>
  );
};

export default Sync;
