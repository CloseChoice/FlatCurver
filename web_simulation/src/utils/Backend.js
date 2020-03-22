import dummy_data from "./dummy_results.json";

class Backend {
  static async runSimulation(payload) {
    const response = await fetch("http://localhost:8051/simulate", {
      method: "POST",
      body: payload, // json input object
      headers: {
        "Content-Type": "application/json"
      }
    });
    const results = await response.json();
    console.log("Backend.runSimulation:", results);
    return results;
  }
}

export default Backend;
