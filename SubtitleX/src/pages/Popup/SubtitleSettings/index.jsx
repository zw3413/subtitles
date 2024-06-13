import React from 'react';
import Upload from './Upload';
import Display from './Display';
import Sync from './Sync';
import Advanced from './Advanced';
import SubtitleX from './SubtitleX';
import { useEffect, useState } from 'react';

const SubtitleSettings = ({ popup, setMenu }) => {
  const [hide, setHide] = useState(true);
  return (
    <div className='subx-text-black'>
    
      <Upload popup={popup} setMenu={setMenu} setHide={setHide}/>
    
      <SubtitleX popup={popup} hide= {hide} setHide={setHide} setMenu={setMenu}/>
      <Display popup={popup} hide= {hide} setHide={setHide} />
      {/* <Sync popup={popup} /> */}
      {/* <Advanced /> */}
    </div>
  );
};

export default SubtitleSettings;
