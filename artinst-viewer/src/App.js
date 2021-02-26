import logo from './logo.svg';
import './App.css';
import React from 'react';
import { BrowserRouter, Route, Link } from 'react-router-dom';
import 'fontsource-roboto';
import VidView from './components/vidview';
import PropTypes from 'prop-types';
import { withStyles, makeStyles } from '@material-ui/core/styles';
import Slider from '@material-ui/core/Slider';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';

function App() {
  const textStyle = {
    marginLeft: '50px',
  };
  return (
      <BrowserRouter>
        <div className="container">
          <div class="grid-container">
            <div class="header"/>
            <div class="content" />           
          </div>
          <div class="header">
              <Typography variant="h3" component="h3" gutterBottom style={textStyle}>
                Art Institute Video Browser
              </Typography>
          </div>
          <div class="content">
              <Route exact path="/" component={VidView} />
          </div>
        </div>
      </BrowserRouter>
  );
}

export default App;
