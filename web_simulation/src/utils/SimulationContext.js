import React, { Component } from "react";
import dummy_data from "./dummy_results.json";
import initial_betas from "./initial_betas.json";
import Actions from "../data/Actions";
import Backend from "./Backend";

const SimulationContext = React.createContext();

export const withSimulation = Component => {
  const WrappedComponent = props => (
    <SimulationContext.Consumer>
      {context => <Component {...props} simulation={context} />}
    </SimulationContext.Consumer>
  );

  WrappedComponent.displayName = `withSimulation(${Component.displayName ||
    Component.name ||
    "Component"})`;

  return WrappedComponent;
};

// this is the main component, it has to be added at the root of the app.
// all components that use withSimulation(...) will have access to it via this.props.Simulation...
class SimulationProvider extends Component {
  constructor(props) {
    super(props);
    this.state = {
      results: dummy_data,
      parameters: {}
    };
  }

  run(actions) {
    let payload = initial_betas;
    for (let region in actions) {
      for (let act of Object.keys(actions[region]).sort(
        c => actions[region][c].date
      )) {
        if (actions[region][act].date !== null) {
          const betaOld = Object.values(payload[region]).slice(-1)[0];
          const actionTemplate = Actions.find(c => c.label === act);
          const beta = actionTemplate.apply(
            betaOld,
            actions[region][act].intensity
          );
          payload[region][
            actions[region][act].date.toISOString().split("T")[0]
          ] = beta;
        }
      }
    }
    console.log("payload:", payload);
    Backend.runSimulation(payload).then(results => {
      this.setState({ results: results, running: false });
      console.log("Backend.runSimulation:", results);
    });
  }

  render() {
    return (
      <SimulationContext.Provider
        value={{
          run: actions => this.run(actions),
          results: this.state.results,
          running: this.state.running
        }}
      >
        {this.props.children}
      </SimulationContext.Provider>
    );
  }
}

export default SimulationProvider;
