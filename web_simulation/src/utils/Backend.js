import dummy_data from "./dummy.json";

class Backend {
  static runSimulation() {
    return new Promise(resolve => {
      setTimeout(() => {
        return dummy_data;
      }, 200);
    });
  }
}

export default Backend;
