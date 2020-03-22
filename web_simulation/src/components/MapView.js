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

function generateMapData(results, selectedRegion, selectedTimeStamp) {
  const mapData = Object.assign(MapData, {});
  for (let region of Regions) {
    if (region.label !== "Deutschland") {
      const timeStampIndex = results[region.label]["Timestamp"].findIndex(
        c => c === selectedTimeStamp.toISOString().split("T")[0]
      );
      setDescriptionOfState(
        mapData,
        region.label,
        `Infiziert: ${Math.round(
          results[region.label]["Infectious"][timeStampIndex]
        )}<br>Genesen: ${Math.round(
          results[region.label]["Recovered"][timeStampIndex]
        )}<br>Verstorben: ${Math.round(
          results[region.label]["Dead"][timeStampIndex]
        )}<br>Empfänglich: ${Math.round(
          results[region.label]["Susceptible"][timeStampIndex]
        )}`
      );
    }
  }
  return mapData;
}

function setColorOfState(mapLayout, name, color) {
  mapLayout.mapbox.layers.find(c => c.source.state === name).color = color;
}

function generateMapLayout(results, selectedRegion, selectedTimeStamp) {
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
    const timeStampIndex = results[region.label]["Timestamp"].findIndex(
      c => c === selectedTimeStamp.toISOString().split("T")[0]
    );
    if (region.label !== "Deutschland") {
      setColorOfState(
        mapLayout,
        region.label,
        results[region.label]["Color"][timeStampIndex]
      );
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

    console.log("MapView Render");

    const curvesData = generateCurveData(results, selectedRegion);
    const mapData = generateMapData(
      results,
      selectedRegion,
      this.props.selectedTimeStamp
    );
    const mapLayout = generateMapLayout(
      results,
      selectedRegion,
      this.props.selectedTimeStamp
    );

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
