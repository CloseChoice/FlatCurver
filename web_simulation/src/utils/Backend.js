import dummy_data from "./dummy_results.json";

class Backend {
  static runSimulation() {
    return new Promise(resolve => {
      setTimeout(() => {
        return resolve(dummy_data);
      }, 2000);
    });
  }
}

export default Backend;
