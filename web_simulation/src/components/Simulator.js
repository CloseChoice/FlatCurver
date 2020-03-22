import React from "react";
import {
  Container,
  Typography,
  Grid,
  Slider,
  Paper,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Toolbar,
  Select,
  MenuItem,
  LinearProgress
} from "@material-ui/core";
import TimeLine from "./TimeLine";
import MapView from "./MapView";

import {
  MuiPickersUtilsProvider,
  KeyboardDatePicker
} from "@material-ui/pickers";
import DateFnsUtils from "@date-io/date-fns";
import Regions from "../data/Regions";
import Actions from "../data/Actions";
import Backend from "../utils/Backend";
import { withSimulation } from "../utils/SimulationContext";

const marks = [
  {
    value: 0,
    label: "0%"
  },
  {
    value: 25,
    label: "20%"
  },
  {
    value: 50,
    label: "50%"
  },
  {
    value: 75,
    label: "75%"
  },
  {
    value: 100,
    label: "100%"
  }
];

function valuetext(value) {
  return `${value}%`;
}

class Simulator extends React.Component {
  constructor(props) {
    super(props);
    const actions = {};
    for (let region of Regions) {
      actions[region.label] = {};
      for (let action of Actions) {
        actions[region.label][action.label] = {
          date: null,
          intensity: 0
        };
      }
    }
    this.state = {
      actions: actions,
      selectedRegion: Regions[0]
    };
    console.log(actions);
  }

  onChangeRegion = event => {
    this.setState({
      selectedRegion: Regions[event.target.value]
    });
  };

  onChangeSlider = async (e, val, selectedRegion, action) => {
    console.log("onChangeSlider:", { val, selectedRegion, action });
    const { actions } = this.state;
    actions[selectedRegion.label][action.label].intensity = val;
    this.setState({ actions });
  };

  onChangeDate = async (date, val, selectedRegion, action) => {
    console.log("onChangeDate:", { date, val, selectedRegion, action });
    const { actions } = this.state;
    actions[selectedRegion.label][action.label].date = date;
    this.setState({ actions });
    this.updateSimulation();
  };

  updateSimulation = async () => {
    this.props.simulation.run(this.state.actions);
  };

  onMapSelectRegion = label => {
    console.log(label);
    this.setState({
      selectedRegion: Regions.find(c => c.label === label)
    });
  };

  render() {
    const { running } = this.props.simulation;
    const { selectedRegion, actions } = this.state;
    return (
      <Container maxWidth="xl" style={{ paddingTop: 30 }}>
        {running && (
          <LinearProgress
            style={{ position: "fixed", top: 0, left: 0, right: 0 }}
          />
        )}
        <Grid container spacing={4} style={{ height: "100%", marginLeft: 0 }}>
          <Grid item container xs={7} spacing={4}>
            <Grid item xs={12}>
              <Typography variant="h4">
                #WirvsVirus Simulator - How to flatten the curve!
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <TableContainer component={Paper} style={{ height: "100%" }}>
                <Toolbar>
                  <Typography style={{ flexGrow: 1 }}></Typography>
                  <Typography style={{ marginRight: 10 }}>
                    <b>Reichweite:</b>
                  </Typography>
                  <Select
                    value={selectedRegion.index}
                    onChange={this.onChangeRegion}
                  >
                    {Regions.map((reg, index) => (
                      <MenuItem key={reg.label} value={index}>
                        {reg.label}
                      </MenuItem>
                    ))}
                  </Select>
                </Toolbar>
                <div style={{ overflow: "auto", height: 620 }}>
                  <Table size="small" style={{ tableLayout: "fixed" }}>
                    <TableHead>
                      <TableRow>
                        <TableCell>
                          <b>Maßnahme</b>
                        </TableCell>
                        <TableCell>
                          <b>Umsetzung</b>
                        </TableCell>
                        <TableCell align="right">
                          <b>Datum der Einsetzung</b>
                        </TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      <MuiPickersUtilsProvider utils={DateFnsUtils}>
                        {Actions.map(action => (
                          <TableRow key={action.label}>
                            <TableCell component="th" scope="row">
                              {action.label}
                            </TableCell>
                            <TableCell
                              style={{ width: 400 }}
                              component="th"
                              scope="row"
                            >
                              {action.slider && (
                                <Slider
                                  value={
                                    actions[selectedRegion.label][action.label]
                                      .intensity || 0
                                  }
                                  onChange={(e, val) =>
                                    this.onChangeSlider(
                                      e,
                                      val,
                                      selectedRegion,
                                      action
                                    )
                                  }
                                  getAriaValueText={valuetext}
                                  aria-labelledby="discrete-slider"
                                  valueLabelDisplay="auto"
                                  step={5}
                                  marks={marks}
                                  min={0}
                                  max={100}
                                />
                              )}
                            </TableCell>
                            <TableCell align="right">
                              <KeyboardDatePicker
                                disableToolbar
                                variant="inline"
                                format="dd/MM/yyyy"
                                margin="normal"
                                value={
                                  actions[selectedRegion.label][action.label]
                                    .date
                                }
                                onChange={(date, val) =>
                                  this.onChangeDate(
                                    date,
                                    val,
                                    selectedRegion,
                                    action
                                  )
                                }
                                autoOk
                                KeyboardButtonProps={{
                                  "aria-label": "change date"
                                }}
                              />
                            </TableCell>
                          </TableRow>
                        ))}
                      </MuiPickersUtilsProvider>
                    </TableBody>
                  </Table>
                </div>
              </TableContainer>
            </Grid>
            <TimeLine />
          </Grid>
          <MapView
            selectedRegion={selectedRegion}
            onSelectRegion={this.onMapSelectRegion}
          />
        </Grid>
      </Container>
    );
  }
}

export default withSimulation(Simulator);
