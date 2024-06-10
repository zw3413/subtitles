import React from 'react';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';

const MenuHeading = (props) => {
  return (
    <Container>
      <Typography color="primary">{props.heading}</Typography>
    </Container>
  );
};

export default MenuHeading;
