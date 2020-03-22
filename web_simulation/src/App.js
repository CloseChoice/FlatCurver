import React from "react";
import "./App.css";
import Simulator from "./components/Simulator";
import { ThemeProvider, createMuiTheme } from "@material-ui/core";
import SimulationProvider from "./utils/SimulationContext";

const theme = createMuiTheme({});

class App extends React.Component {
  state = { value: 0, previous: 0 };

  render() {
    return (
      <ThemeProvider theme={theme}>
        <div className="App">
          <SimulationProvider>
            <Simulator />
          </SimulationProvider>
        </div>
      </ThemeProvider>
    );
  }
}

export default App;
