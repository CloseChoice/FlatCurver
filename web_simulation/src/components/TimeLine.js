import React from "react";
import { Grid, Paper, withStyles, withTheme } from "@material-ui/core";
import HorizontalTimeline from "react-horizontal-timeline";

function createTimeStamps() {
  var now = new Date(2020, 6, 1);
  var daysOfYear = [];
  for (var d = new Date(2020, 1, 1); d <= now; d.setDate(d.getDate() + 2)) {
    daysOfYear.push(new Date(d));
  }

  return daysOfYear;
}

const VALUES = createTimeStamps();

class TimeLine extends React.Component {
  state = { value: 20, previous: 19 };

  componentDidMount() {
    this.props.onSelectTimeStamp(VALUES[20]);
  }

  render() {
    const { theme } = this.props;
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
              style={{ foreground: theme.palette.primary }}
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
