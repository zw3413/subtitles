import React, { useState, useEffect } from 'react';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemSecondaryAction from '@mui/material/ListItemSecondaryAction';
import IconButton from '@mui/material/IconButton';
import AddCircleIcon from '@mui/icons-material/AddCircle';
import RemoveCircleIcon from '@mui/icons-material/RemoveCircle';
import MenuHeading from '../MenuHeading';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import PaletteIcon from '@mui/icons-material/Palette';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import VisibilityIcon from '@mui/icons-material/Visibility';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
const Display = ({ popup, hide, setHide }) => {
  const [listening, setListening] = useState(false);
  const [direction, setDirection] = useState(false);
  const [syncValue, setSyncValue] = useState(0);

  const colors = ["grey", "blue", "yellow"]
  const [color, setColor] = useState('grey');
  const possible =["subx-bg-grey-200","subx-bg-blue-200","subx-bg-yellow-200" ]

  function displaySettingsHandler(action) {
    if (popup) {
      // Send message to content script (this file but content script)
      chrome.tabs.query({ currentWindow: true, active: true }, function (tab) {
        chrome.tabs.sendMessage(tab[0].id, { displaySettings: action });
      });
    } else {
      // Dispatch event
      const displaySettings = new CustomEvent('displaySettings', {
        detail: action,
      });
      document.dispatchEvent(displaySettings);
    }
  }

  function handleSyncValueChange() {
    //setSyncValue(event.target.value === '' ? '' : Number(event.target.value));
    let passSyncValue = syncValue
    if (passSyncValue < 0) {
      passSyncValue = passSyncValue * -1
      setDirection(true)
    } else {
      setDirection(false)
    }

    handleSync({ syncValue: passSyncValue, syncLater: direction })
  };


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

  if (!listening) {
    setListening(true);
    if (!popup) {
      // Listening for messages from the popup (this file but popup)
      chrome.runtime.onMessage.addListener((msg) => {
        if (msg.displaySettings) {
          displaySettingsHandler(msg.displaySettings);
        }
        if (msg.syncValue) {
          // This time calling handleSync from the content script instead of from the popup
          handleSync(msg);
        }
      });

    }
  }

  useEffect(() => {
    handleSyncValueChange()
  }, [syncValue])

  useEffect(() => {
    if (hide) {
      displaySettingsHandler('hide-hide')
    } else {
      displaySettingsHandler('hide-show')
    }
  }, [hide])
  
  return <>
    {/* <MenuHeading heading="Display:" /> */}
    <Container className="subx-my-4 subx-text-[16px]">
      <List component="nav" aria-label="main mailbox folders">
      <ListItem button>
          <ListItemText style={{ color: 'black' }} >
            {chrome.i18n.getMessage("synchronize")} {syncValue}{chrome.i18n.getMessage("second")}</ListItemText>
          <ListItemSecondaryAction>

            <IconButton
              onClick={() => { setSyncValue(syncValue - 1) }}
              edge="end"
              aria-label="opacity-plus"
              size="large">
              <RemoveCircleIcon />
            </IconButton>
            <IconButton
              onClick={() => { setSyncValue(syncValue + 1) }}
              edge="end"
              aria-label="opacity-plus"
              size="large">      <AddCircleIcon /></IconButton>

          </ListItemSecondaryAction>

        </ListItem>
        <ListItem button>
          <ListItemText style={{ color: 'black' }} primary={chrome.i18n.getMessage('fontSize')} />
          <ListItemSecondaryAction>
            <IconButton
              onClick={(event) => {displaySettingsHandler('font-smaller');event.preventDefault();event.stopPropagation()}}
              edge="end"
              aria-label="font-smaller"
              size="large">
              <RemoveCircleIcon />
            </IconButton>
            <IconButton
              onClick={() => displaySettingsHandler('font-bigger')}
              edge="end"
              aria-label="font-bigger"
              size="large">
              <AddCircleIcon />
            </IconButton>
          </ListItemSecondaryAction>
        </ListItem>
        <ListItem button>
          <ListItemText style={{ color: 'black' }} primary={chrome.i18n.getMessage("background")} />
          <ListItemSecondaryAction>

            <IconButton
              onClick={() => displaySettingsHandler('opacity-minus')}
              edge="end"
              aria-label="opacity-minus"
              size="large">
              <RemoveCircleIcon />
            </IconButton>
            <IconButton
              onClick={() => displaySettingsHandler('opacity-plus')}
              edge="end"
              aria-label="opacity-plus"
              size="large">
              <AddCircleIcon />
            </IconButton>
          </ListItemSecondaryAction>
        </ListItem>

       

        {/* <ListItem button>
          <ListItemText style={{ color: 'black' }} >
            Color </ListItemText>
          <ListItemSecondaryAction>
            <Select
              labelId="demo-simple-select-label"
              id="demo-simple-select"
              value={color}
              className={`subx-bg-${color}-200 subx-min-w-[80px] subx-text-center`}
             onChange={e => {setColor(e.target.value)}}
            >
              {
                colors.map((color) => {
                  return <MenuItem className={`subx-min-w-[80px] subx-text-center`} value={color}>{color}</MenuItem>
                })
              }
            </Select>
          </ListItemSecondaryAction>
        </ListItem> */}


        <ListItem button>
          <ListItemText style={{ color: 'black' }} >
            {chrome.i18n.getMessage('hideSubtitle')} </ListItemText>
          <ListItemSecondaryAction>
            <IconButton
              onClick={() => { setHide(!hide) }}
              edge="end"
              aria-label="opacity-plus"
              size="large">
              {hide ? <VisibilityOffIcon /> : <VisibilityIcon />}
            </IconButton>
          </ListItemSecondaryAction>

        </ListItem>
      </List>
    </Container>
  </>;
};

export default Display;
