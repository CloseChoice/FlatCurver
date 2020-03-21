import React from "react";
import "./App.css";
import { withStyles, Container, Typography, Grid } from "@material-ui/core";
import HorizontalTimeline from "react-horizontal-timeline";

function createTimeStamps() {
  var now = new Date();
  var daysOfYear = [];
  for (var d = new Date(2020, 1, 1); d <= now; d.setDate(d.getDate() + 1)) {
    daysOfYear.push(new Date(d));
  }

  return daysOfYear;
}

const VALUES = createTimeStamps();

class App extends React.Component {
  state = { value: 0, previous: 0 };

  render() {
    return (
      <div className="App">
        <Grid
          container
          spacing={4}
          style={{ background: "#fff", height: "150px" }}
        ></Grid>
        <Grid
          container
          spacing={4}
          style={{ height: "calc(100vh - 100px - 300px)" }}
        >
          <Grid
            item
            xs={4}
            style={{ background: "#555", height: "100%" }}
          ></Grid>
          <Grid item xs={8} style={{ background: "#999" }}></Grid>
        </Grid>
        <Grid
          container
          spacing={4}
          style={{ background: "#fff", height: "300px" }}
        >
          <div
            style={{
              width: "calc(100% - 50px)",
              height: "100px",
              margin: "auto"
            }}
          >
            <HorizontalTimeline
              labelWidth={50}
              linePadding={50}
              index={this.state.value}
              indexClick={index => {
                this.setState({ value: index, previous: this.state.value });
              }}
              values={VALUES}
            />
          </div>
        </Grid>
      </div>
    );
  }
}

export default App;
