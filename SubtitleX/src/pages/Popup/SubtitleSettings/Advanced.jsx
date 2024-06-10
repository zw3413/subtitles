import React, { useState } from 'react';
import MenuHeading from '../MenuHeading';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemSecondaryAction from '@mui/material/ListItemSecondaryAction';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';

const Advanced = () => {
  const [silenceIndicator, setSilenceIndicator] = useState(false);
  const [editMode, setEditMode] = useState(false);

  // Retrieving the silence and editMode settings from chrome storage
  chrome.storage.sync.get(null, function (storage) {
    if (storage.silence !== undefined && silenceIndicator !== storage.silence) {
      setSilenceIndicator(storage.silence);

    } else if (storage.editMode !== undefined && editMode !== storage.editMode) {
      setEditMode(storage.editMode)
    }
  });

  function silenceSwitchHandler(e) {
    e.preventDefault();
    setSilenceIndicator(!silenceIndicator);
    chrome.storage.sync.set({
      silence: !silenceIndicator,
    });
  }

  function editModeHandler(e) {
    e.preventDefault();
    setEditMode(!editMode);
    chrome.storage.sync.set({
      editMode: !editMode,
    });
  }

  return (
    <>
      <MenuHeading heading="Advanced:" />
      <List component="nav" aria-label="main mailbox folders">
        <ListItem button>
          <ListItemText
            style={{ color: 'black' }}
            primary="Silence Indicator"
          />
          <ListItemSecondaryAction>
            <FormControlLabel
              control={<Switch checked={silenceIndicator} />}
              onClick={silenceSwitchHandler}
            />
          </ListItemSecondaryAction>
        </ListItem>
        <ListItem button>
          <ListItemText
            style={{ color: 'black' }}
            primary="Edit Mode"
          />
          <ListItemSecondaryAction>
            <FormControlLabel
              control={<Switch checked={editMode} />}
              onClick={editModeHandler}
            />
          </ListItemSecondaryAction>
        </ListItem>
      </List>
    </>
  );
};

export default Advanced;
