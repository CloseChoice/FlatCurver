import React from "react";
import "./App.css";
import {
  withStyles,
  Container,
  Typography,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Checkbox,
  Slider
} from "@material-ui/core";
import FolderIcon from "@material-ui/icons/Folder";
import Dashboard from "./components/Dashboard";

class App extends React.Component {
  state = { value: 0, previous: 0 };

  render() {
    return (
      <div className="App">
        <Dashboard />
      </div>
    );
  }
}

export default App;
