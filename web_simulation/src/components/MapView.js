import React from "react";
import { Grid, Paper } from "@material-ui/core";
import PropTypes from "prop-types";

import { MapData, MapLayout } from "../data/MapViewLayout";

import Plotly from "plotly.js-mapbox-dist";
import createPlotlyComponent from "react-plotly.js/factory";
import { withSimulation } from "../utils/SimulationContext";
import Regions from "../data/Regions";
const Plot = createPlotlyComponent(Plotly);

//https://plot.ly/create/?fid=empet:15047

const config = {
  showLink: true,
  linkText: "Export to plot.ly",
  mapboxAccessToken:
    "pk.eyJ1IjoiY2hyaWRkeXAiLCJhIjoiY2lxMnVvdm5iMDA4dnhsbTQ5aHJzcGs0MyJ9.X9o_rzNLNesDxdra4neC_A"
};

function generateCurveData(results, selectedRegion) {
  return [
    {
      x: results[selectedRegion.label]["Timestamp"],
      y: results[selectedRegion.label]["Susceptible"],
      type: "scatter",
      name: "Empfänglich",
      mode: "lines",
      marker: { color: "orange" }
    },
    {
      x: results[selectedRegion.label]["Timestamp"],
      y: results[selectedRegion.label]["Dead"],
      type: "scatter",
      name: "Verstorben",
      mode: "lines",
      marker: { color: "black" }
    },
    {
      x: results[selectedRegion.label]["Timestamp"],
      y: results[selectedRegion.label]["Infectious"],
      type: "scatter",
      name: "Infiziert",
      mode: "lines",
      marker: { color: "red" }
    },
    {
      x: results[selectedRegion.label]["Timestamp"],
      y: results[selectedRegion.label]["Recovered"],
      type: "scatter",
      name: "Genesen",
      mode: "lines",
      marker: { color: "green" }
    }
  ];
}

function setDescriptionOfState(mapData, name, text) {
  const index = mapData[0].text.findIndex(c => c.startsWith(name));
  mapData[0].text[index] = `${name}<br>${text}`;
}

function generateMapData(results, selectedRegion) {
  const mapData = Object.assign(MapData, {});
  console.log(mapData);
  setDescriptionOfState(
    mapData,
    "Bayern",
    `Empfänglich: ${2}<br>Verstorben: ${2}<br>Infiziert: ${2}<br>Genesen: ${2}<br>`
  );
  return mapData;
}

function setColorOfState(mapLayout, name, color) {
  mapLayout.mapbox.layers.find(c => c.source.state === name).color = color;
}

function generateMapLayout(results, selectedRegion) {
  const mapLayout = Object.assign(MapLayout, {
    width: 750,
    height: 580,
    title: "",
    margin: {
      l: 0,
      r: 0,
      t: 5,
      b: 0
    }
  });

  for (let region of Regions) {
    if (region.label !== "Deutschland") {
      console.log(region.label);
      setColorOfState(mapLayout, region.label, "#ff0000");
    }
  }

  return mapLayout;
}

class MapView extends React.Component {
  onMapClick = e => {
    let region = null;
    try {
      region = e.points[0].text.split("<br>")[0];
    } catch {}

    console.log(region);

    if (region !== null) this.props.onSelectRegion(region);
  };

  render() {
    const { results } = this.props.simulation;
    const { selectedRegion } = this.props;

    const curvesData = generateCurveData(results, selectedRegion);
    const mapData = generateMapData(results, selectedRegion);
    const mapLayout = generateMapLayout(results, selectedRegion);

    return (
      <Grid item xs={5} container>
        <Grid item xs={12} style={{ marginBottom: 32 }}>
          <Paper>
            <Plot
              data={curvesData}
              layout={{
                width: 750,
                height: 260,
                title: `Simulierter Verlauf in ${selectedRegion.label}`,
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
        <Grid item xs={12}>
          <Paper>
            <Plot
              data={mapData}
              frames={[]}
              layout={mapLayout}
              config={config}
              onClick={this.onMapClick}
            />
          </Paper>
        </Grid>
      </Grid>
    );
  }
}

MapView.propTypes = {
  selectedRegion: PropTypes.object.isRequired,
  simulation: PropTypes.object.isRequired,
  onSelectRegion: PropTypes.func.isRequired
};

export default withSimulation(MapView);
