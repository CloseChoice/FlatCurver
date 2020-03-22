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

const Actions = [
  "Schulen / Kitas schließen",
  "Läden schließen",
  "Ausgangsperre",
  "Homeoffice",
  "Restaurant schließen",
  "Kulturprogramme schließen",
  "Grenzen schließen"
];

class Dashboard extends React.Component {
  state = { value: 0, previous: 0 };

  render() {
    return (
      <Container maxWidth="xl" style={{ paddingTop: 30 }}>
        <Grid container spacing={4} style={{ height: "100%" }}>
          <Grid item container xs={8} spacing={4}>
            <Grid item xs={12}>
              <Typography variant="h4">Simulator</Typography>
            </Grid>
            <Grid item xs={12}>
              <TableContainer component={Paper}>
                <Toolbar>
                  <Typography style={{ flexGrow: 1 }}></Typography>
                  <Select value={"Baden-Württemberg"}>
                    <MenuItem value={"Deutschland"}>Deutschland</MenuItem>
                    <MenuItem value={"Baden-Württemberg"}>
                      Baden-Württemberg
                    </MenuItem>
                    <MenuItem value={"Bayern"}>Bayern</MenuItem>
                    <MenuItem value={"Hessen"}>Hessen</MenuItem>
                  </Select>
                </Toolbar>
                <Table size="small" aria-label="simple table">
                  <TableHead>
                    <TableRow>
                      <TableCell>Maßnahme</TableCell>
                      <TableCell>Intensität</TableCell>
                      <TableCell align="right">Datum eingesetzt</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <MuiPickersUtilsProvider utils={DateFnsUtils}>
                      {Actions.map(actionTitle => (
                        <TableRow key={actionTitle}>
                          <TableCell component="th" scope="row">
                            {actionTitle}
                          </TableCell>
                          <TableCell
                            style={{ width: 400 }}
                            component="th"
                            scope="row"
                          >
                            <Slider
                              defaultValue={30}
                              aria-labelledby="discrete-slider"
                              valueLabelDisplay="auto"
                              step={10}
                              marks
                              min={10}
                              max={100}
                            ></Slider>
                          </TableCell>
                          <TableCell align="right">
                            <KeyboardDatePicker
                              disableToolbar
                              variant="inline"
                              format="MM/dd/yyyy"
                              margin="normal"
                              id="date-picker-inline"
                              label="Date picker inline"
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
          <MapView />
        </Grid>
      </Container>
    );
  }
}

export default Dashboard;
