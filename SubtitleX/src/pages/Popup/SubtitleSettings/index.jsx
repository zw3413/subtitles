import React from 'react';
import Upload from './Upload';
import Display from './Display';
import Sync from './Sync';
import Advanced from './Advanced';
import SubtitleX from './SubtitleX';
const SubtitleSettings = ({ popup, setMenu }) => {
  return (
    <div className='subx-text-black'>
    
      <Upload popup={popup} setMenu={setMenu} />
      <SubtitleX popup={popup} />
      <Display popup={popup} />
      {/* <Sync popup={popup} /> */}
      {/* <Advanced /> */}
    </div>
  );
};

export default SubtitleSettings;
