import React, {useState, useEffect} from 'react';
import MenuHeading from './MenuHeading';
import KeyboardIcon from '@mui/icons-material/Keyboard';
import FeedbackIcon from '@mui/icons-material/Feedback';
import InfoIcon from '@mui/icons-material/Info';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemSecondaryAction from '@mui/material/ListItemSecondaryAction';
import IconButton from '@mui/material/IconButton';
import openPage from './openPage';
import {findUser} from './Common';
import AccountBoxIcon from '@mui/icons-material/AccountBox';

const GeneralSection = ({ setDisplayShortcuts, popup }) => {
  const [userName, setUsername] = useState('')
  const [subscribed, setSubscribed] = useState(false)

  useEffect(()=>{
    findUser().then((user)=>{
      console.log(user)
      let un = user.name? user.name:user.email
      setUsername(un?un:'')
      setSubscribed(user.hasSub || user.subscribed)
    })
  })

  return <>
    {/* <MenuHeading heading="General:" /> */}
    <List component="nav" aria-label="main mailbox folders">
      {/* <ListItem button>
        <ListItemText
          onClick={() => setDisplayShortcuts(true)}
          style={{ color: 'black' }}
          primary="Shortcuts"
        />
        <ListItemSecondaryAction>
          <IconButton edge="end" aria-label="shortcuts">
            <KeyboardIcon />
          </IconButton>
        </ListItemSecondaryAction>
      </ListItem> */}
       <ListItem
        button
        onClick={() =>
          openPage(
            popup,
            'https://www.subtitlex.xyz/Member'
          )
        }
      >
        {/* <ListItemText style={{ color: 'black' }}  >{userName.length>0?userName:"Login"}</ListItemText> */}
        <ListItemText style={{ color: 'black' }}  >{subscribed ? "Profile":"Subscribe"}</ListItemText>
        <ListItemSecondaryAction>
          <IconButton edge="end" aria-label="feedback" size="large">
            <AccountBoxIcon />
          </IconButton>
        </ListItemSecondaryAction>
      </ListItem>

      <ListItem
        button
        onClick={() =>
          openPage(
            popup,
            'https://www.subtitlex.xyz/Extension'
          )
        }
      >
        <ListItemText style={{ color: 'black' }} primary="Feedback" />
        <ListItemSecondaryAction>
          <IconButton edge="end" aria-label="feedback" size="large">
            <FeedbackIcon />
          </IconButton>
        </ListItemSecondaryAction>
      </ListItem>
      {/* <ListItem
        button
        onClick={() =>
          openPage(
            popup,
            'https://github.com/gignupg/Movie-Subtitles-Chrome-Extension'
          )
        }
      >
        <ListItemText style={{ color: 'black' }} primary="About" />
        <ListItemSecondaryAction>
          <IconButton edge="end" aria-label="about">
            <InfoIcon />
          </IconButton>
        </ListItemSecondaryAction>
      </ListItem> */}
    </List>
  </>;
};

export default GeneralSection;
