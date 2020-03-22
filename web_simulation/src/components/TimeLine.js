import React from "react";
import { Grid } from "@material-ui/core";
import HorizontalTimeline from "react-horizontal-timeline";

function createTimeStamps() {
  var now = new Date();
  var daysOfYear = [];
  for (var d = new Date(2020, 1, 1); d <= now; d.setDate(d.getDate() + 2)) {
    daysOfYear.push(new Date(d));
  }

  return daysOfYear;
}

const VALUES = createTimeStamps();

class TimeLine extends React.Component {
  state = { value: 0, previous: 0 };

  render() {
    return (
      <Grid item xs={12} style={{ eight: "200px" }}>
        <div
          style={{
            width: "calc(100% - 50px)",
            height: "100px",
            margin: "auto"
          }}
        >
          <HorizontalTimeline
            labelWidth={50}
            linePadding={10}
            index={this.state.value}
            indexClick={index => {
              this.setState({ value: index, previous: this.state.value });
            }}
            values={VALUES}
          />
        </div>
      </Grid>
    );
  }
}

export default TimeLine;
