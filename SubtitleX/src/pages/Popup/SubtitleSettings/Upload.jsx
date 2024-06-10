import React, { useState,useEffect } from 'react';
import { styled } from '@mui/material/styles';
import PublishIcon from '@mui/icons-material/Publish';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import { getSeed } from './SubtitleX'
import { uploadSubtitleFile } from '../Common'


const InvisibleInput = styled('input')({
  display: 'none',
});

const Upload = ({ popup, setMenu, setHide }) => {
  const [listening, setListening] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);

  function invisibleUploadHandler(e) {
    const file = e.target.files[0];
    const fileUpload = new CustomEvent('fileUpload', { detail: file });
    document.dispatchEvent(fileUpload);
    setMenu(false);
    //上传subtitle
    setUploadFile(file)
  }
  useEffect(() => {
    if(uploadFile && uploadFile.name){
      const seed = getSeed()
      uploadSubtitleFile(seed, uploadFile)
      setHide(false)
    }
  }, [uploadFile])

  function uploadButtonHandler() {
    if (popup) {
      // Sending message to the content script, then opening the file upload window from there
      chrome.tabs.query({ currentWindow: true, active: true }, function (tab) {
        chrome.tabs.sendMessage(tab[0].id, { fileUpload: true });
      });
    } else {
      document.getElementById('movie-subtitles-file-upload').click();
    }
  }

  if (!popup && !listening) {
    setListening(true);
    chrome.runtime.onMessage.addListener((msg) => {
      if (msg.fileUpload) {
        document.getElementById('movie-subtitles-file-upload').click();
      }
    });
  }

  return (
    <Container className='subx-my-4'>
      <InvisibleInput
        onChange={invisibleUploadHandler}
        type="file"
        id="movie-subtitles-file-upload"
      />
      <Button

        style={{ width: "100%", height: "56px", backgroundColor:"#20e4ff" }}
        onClick={uploadButtonHandler}
        variant="contained"
        color="secondary"
        endIcon={<PublishIcon />}
      >
        Load Subtitles
      </Button>
    </Container>

    // <Box mb={4} mt={2}>
    //   <Grid container justifyContent="center" my={8}>
    //     <InvisibleInput
    //       onChange={invisibleUploadHandler}
    //       type="file"
    //       id="movie-subtitles-file-upload"
    //     />
    //     <Button
    //       onClick={uploadButtonHandler}
    //       variant="contained"
    //       color="secondary"
    //       endIcon={<PublishIcon />}
    //     >
    //       Load Subtitles
    //     </Button>
    //   </Grid>
    // </Box>
  );
};

export default Upload;
