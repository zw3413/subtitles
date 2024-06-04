import React, { useState, useEffect } from 'react';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import ListItemSecondaryAction from '@material-ui/core/ListItemSecondaryAction';
import IconButton from '@material-ui/core/IconButton';
import AddCircleIcon from '@material-ui/icons/AddCircle';
import RemoveCircleIcon from '@material-ui/icons/RemoveCircle';
import MenuHeading from '../MenuHeading';
import Box from '@material-ui/core/Box';
import Container from '@material-ui/core/Container';
import PaletteIcon from '@material-ui/icons/Palette';
import VisibilityOffIcon from '@material-ui/icons/VisibilityOff';
import VisibilityIcon from '@material-ui/icons/Visibility';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
const Display = ({ popup }) => {
  const [listening, setListening] = useState(false);
  const [direction, setDirection] = useState(false);
  const [syncValue, setSyncValue] = useState(0);
  const [hide, setHide] = useState(false);
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
  
  return (
    <>
      {/* <MenuHeading heading="Display:" /> */}
      <Container className="subx-my-4">
        <List component="nav" aria-label="main mailbox folders">
          <ListItem button>
            <ListItemText style={{ color: 'black' }} primary="Font Size" />
            <ListItemSecondaryAction>
              <IconButton
                onClick={() => displaySettingsHandler('font-smaller')}
                edge="end"
                aria-label="font-smaller"
              >
                <RemoveCircleIcon />
              </IconButton>
              <IconButton
                onClick={() => displaySettingsHandler('font-bigger')}
                edge="end"
                aria-label="font-bigger"
              >
                <AddCircleIcon />
              </IconButton>
            </ListItemSecondaryAction>
          </ListItem>
          <ListItem button>
            <ListItemText style={{ color: 'black' }} primary="Background" />
            <ListItemSecondaryAction>

              <IconButton
                onClick={() => displaySettingsHandler('opacity-minus')}
                edge="end"
                aria-label="opacity-minus"
              >
                <RemoveCircleIcon />
              </IconButton>
              <IconButton
                onClick={() => displaySettingsHandler('opacity-plus')}
                edge="end"
                aria-label="opacity-plus"
              >
                <AddCircleIcon />
              </IconButton>
            </ListItemSecondaryAction>
          </ListItem>

          <ListItem button>
            <ListItemText style={{ color: 'black' }} >
              Sync {syncValue}s</ListItemText>
            <ListItemSecondaryAction>

              <IconButton
                onClick={() => { setSyncValue(syncValue - 1) }}
                edge="end"
                aria-label="opacity-plus"
              >
                <RemoveCircleIcon />
              </IconButton>
              <IconButton
                onClick={() => { setSyncValue(syncValue + 1) }}
                edge="end"
                aria-label="opacity-plus"
              >      <AddCircleIcon /></IconButton>

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
              Hide Subtitle </ListItemText>
            <ListItemSecondaryAction>
              <IconButton
                onClick={() => { setHide(!hide) }}
                edge="end"
                aria-label="opacity-plus"
              >
                {hide ? <VisibilityOffIcon /> : <VisibilityIcon />}
              </IconButton>
            </ListItemSecondaryAction>

          </ListItem>
        </List>
      </Container>
    </>
  );
};

export default Display;
