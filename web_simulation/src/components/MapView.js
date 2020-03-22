import React from "react";
import { Grid, Paper } from "@material-ui/core";
import PropTypes from "prop-types";

import MapViewLayout from "../data/MapViewLayout";

import Plotly from "plotly.js-mapbox-dist";
import createPlotlyComponent from "react-plotly.js/factory";
import { withSimulation } from "../utils/SimulationContext";
const Plot = createPlotlyComponent(Plotly);

//https://plot.ly/create/?fid=empet:15047

const config = {
  showLink: true,
  linkText: "Export to plot.ly",
  mapboxAccessToken:
    "pk.eyJ1IjoiY2hyaWRkeXAiLCJhIjoiY2lxMnVvdm5iMDA4dnhsbTQ5aHJzcGs0MyJ9.X9o_rzNLNesDxdra4neC_A"
};
const map_data = [
  {
    uid: "05437872-56e9-4feb-abd3-79536cb1dd8e",
    mode: "markers",
    type: "scattermapbox",
    lat: [
      48.53798784334733,
      48.94917269695629,
      52.95,
      52.502299698009296,
      52.765431393186596,
      53.54610462404504,
      50.60321670836851,
      53.7535394556047,
      53.19920119721645,
      51.47995445845961,
      49.91548638774605,
      49.38363449476495,
      51.05032936763161,
      52.01060815844672,
      54.182325455715194,
      50.90389419311208
    ],
    lon: [
      9.049518423658956,
      11.418027577497131,
      13.2,
      13.402948501480669,
      9.161108235507873,
      10.024470557873288,
      9.028805533680368,
      12.549970296944396,
      8.74885429375113,
      7.562839874438013,
      7.447768558468357,
      6.955542369514458,
      13.347113513341009,
      11.701732969476758,
      9.813437574822748,
      11.023180940292486
    ],
    marker: { size: 6, color: "white", opacity: 0 },
    text: [
      "Baden-Württemberg<br>Population: 10075500",
      "Bayern<br>Population: 12542000",
      "Brandenburg<br>Population: 2500000",
      "Berlin<br>Population: 3469000",
      "Niedersachsen<br>Population: 7914000",
      "Hamburg<br>Population: 1788000",
      "Hessen<br>Population: 6066000",
      "Mecklenburg-Vorpommern<br>Population: 1639000",
      "Bremen<br>Population: 661000",
      "Nordrhein-Westfalen<br>Population: 17837000",
      "Rheinland-Pfalz<br>Population: 4052803",
      "Saarland<br>Population: 1018000",
      "Sachsen<br>Population: 4143000",
      "Sachsen-Anhalt<br>Population: 2331000",
      "Schleswig-Holstein<br>Population: 2833000",
      "Thüringen<br>Population: 2231000"
    ],
    hoverinfo: "text",
    showlegend: false
  }
];

class MapView extends React.Component {
  render() {
    const { results } = this.props.simulation;
    const { selectedRegion } = this.props;

    return (
      <Grid item xs={4} container>
        <Grid item xs={12} style={{ marginBottom: 32 }}>
          <Paper>
            <Plot
              data={map_data}
              frames={[]}
              layout={Object.assign(MapViewLayout, {
                width: 590,
                height: 580,
                title: "",
                margin: {
                  l: 0,
                  r: 0,
                  t: 5,
                  b: 0
                }
              })}
              config={config}
            />
          </Paper>
        </Grid>
        <Grid item xs={12}>
          <Paper>
            <Plot
              data={[
                {
                  x: results[selectedRegion.label]["Timestamp"],
                  y: results[selectedRegion.label]["Susceptible"],
                  type: "scatter",
                  name: "Susceptible",
                  mode: "lines",
                  marker: { color: "orange" }
                },
                {
                  x: results[selectedRegion.label]["Timestamp"],
                  y: results[selectedRegion.label]["Dead"],
                  type: "scatter",
                  name: "Dead",
                  mode: "lines",
                  marker: { color: "black" }
                },
                {
                  x: results[selectedRegion.label]["Timestamp"],
                  y: results[selectedRegion.label]["Infectious"],
                  type: "scatter",
                  name: "Infectious",
                  mode: "lines",
                  marker: { color: "red" }
                },
                {
                  x: results[selectedRegion.label]["Timestamp"],
                  y: results[selectedRegion.label]["Recovered"],
                  type: "scatter",
                  name: "Recovered",
                  mode: "lines",
                  marker: { color: "green" }
                }
              ]}
              layout={{
                width: 580,
                height: 260,
                title: "Epidemie Verlauf",
                margin: {
                  l: 30,
                  r: 0,
                  t: 50,
                  b: 30
                }
              }}
            />
          </Paper>
        </Grid>
      </Grid>
    );
  }
}

MapView.propTypes = {
  selectedRegion: PropTypes.object.isRequired,
  simulation: PropTypes.object.isRequired
};

export default withSimulation(MapView);
