import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardActionArea from '@material-ui/core/CardActionArea';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import CardMedia from '@material-ui/core/CardMedia';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';

const useStyles = makeStyles({
  root: {
    maxWidth: 345,
  },
});

/*
async function getData(url = '') {
  // Default options are marked with *
  const response = await fetch(url, {
  method: 'GET', // *GET, POST, PUT, DELETE, etc.
  mode: 'cors', // no-cors, *cors, same-origin
  cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
  credentials: 'same-origin', // include, *same-origin, omit
  headers: {
    'Accept': 'application/json'
  }
  }).then( response => this.setState((state, props) => ({
    artwork: response.json(),
  })))
}
*/

//directors = ""; (async () => {
//  directors = await fetch('http://127.0.0.1:8000/viddetails').then(response => response.json());
//})();

export default function VidView() {
  const classes = useStyles();
  function getData(url = "") {
    //artwork = fetch("http://127.0.0.1:8000/viddetails").then(response => response.json());
    fetch(url)
    .then(
      function(response) {
        if (response.status !== 200) {
          console.log('Looks like there was a problem. Status Code: ' +
            response.status);
          return;
        }
  
        // Examine the text in the response
        response.json().then(function(data) {
          return data.title;
        });
      }
    )
    .catch(function(err) {
      console.log('Fetch Error :-S', err);
    });
  
  }
  
  
  return (
    <Card className={classes.root}>
      <CardActionArea>
        <CardMedia
          component="video"
          alt="Nighthawks"
          height="140"
          image="http://localhost:8000/vidtest"
          title="Edward Hopper"
          controls
        />
        <CardContent>
          <Typography gutterBottom variant="h5" component="h2">
            {getData('http://127.0.0.1:8000/viddetails')}
          </Typography>
          <Typography variant="body2" color="textSecondary" component="p">
            {getData('http://127.0.0.1:8000/viddetails')}
          </Typography>
        </CardContent>
      </CardActionArea>
      <CardActions>
        <Button size="small" color="primary">
          Share
        </Button>
        <Button size="small" color="primary">
          Learn More
        </Button>
      </CardActions>
    </Card>
  );
}