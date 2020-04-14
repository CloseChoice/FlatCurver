import React from "react";
import { Grid, Paper, withStyles, withTheme } from "@material-ui/core";
import HorizontalTimeline from "react-horizontal-timeline";

function createTimeStamps() {
  var later = new Date(2020, 6, 1);
  var daysOfYear = [];
  for (var d = new Date(2020, 1, 1); d <= later; d.setDate(d.getDate() + 1)) {
    daysOfYear.push(new Date(d));
  }

  return daysOfYear;
}

const VALUES = createTimeStamps();

const start_index = Math.floor(
  (new Date().getTime() - VALUES[0].getTime()) / (1000 * 3600 * 24)
);

class TimeLine extends React.Component {
  state = { value: start_index, previous: start_index - 1 };

  componentDidMount() {
    this.props.onSelectTimeStamp(VALUES[start_index]);
  }

  render() {
    const { theme } = this.props;
    console.log("theme.palette.primary", theme.palette.primary);
    return (
      <Grid item xs={12} style={{ eight: "200px" }}>
        <Paper>
          <div
            className="timelineDiv"
            style={{
              width: "calc(100% - 50px)",
              height: 80,
              paddingTop: 10,
              margin: "auto"
            }}
          >
            <HorizontalTimeline
              styles={{
                foreground: theme.palette.primary.main,
                outline: "#fff",
                background: "#424242"
              }}
              labelWidth={50}
              linePadding={10}
              index={this.state.value}
              indexClick={index => {
                this.setState({ value: index, previous: this.state.value });
                this.props.onSelectTimeStamp(VALUES[index]);
              }}
              values={VALUES}
            />
          </div>
        </Paper>
      </Grid>
    );
  }
}

export default withTheme(TimeLine);
