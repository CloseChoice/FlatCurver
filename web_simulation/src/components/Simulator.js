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
  MenuItem
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
          data: null,
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

  onChangeSlider = (e, val, selectedRegion, action) => {
    console.log("onChangeSlider:", { val, selectedRegion, action });
    const { actions } = this.state;
    actions[selectedRegion.label][action.label].intensity = val;
    this.setState({ actions });
  };

  updateSimulation = async () => {
    await Backend.runSimulation();
  };

  render() {
    const { selectedRegion, actions } = this.state;
    return (
      <Container maxWidth="xl" style={{ paddingTop: 30 }}>
        <Grid container spacing={4} style={{ height: "100%", marginLeft: 0 }}>
          <Grid item container xs={8} spacing={4}>
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
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>
                        <b>Maßnahme</b>
                      </TableCell>
                      <TableCell>
                        <b>Umsetzung</b>
                      </TableCell>
                      <TableCell align="right">
                        <b>Datum eingesetzt</b>
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
                                step={10}
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
                              format="MM/dd/yyyy"
                              margin="normal"
                              label="Datum der Einsetzung"
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
              </TableContainer>
            </Grid>
            <TimeLine />
          </Grid>
          <MapView selectedRegion={selectedRegion} />
        </Grid>
      </Container>
    );
  }
}

export default withSimulation(Simulator);
