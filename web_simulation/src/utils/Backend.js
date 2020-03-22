const BACKEND_URL = "http://localhost:8051/simulate";
//const BACKEND_URL = "https://flatcurverapi.eu.pythonanywhere.com/simulate";

class Backend {
  static async runSimulation(payload) {
    // "http://localhost:8051/simulate"
    const response = await fetch(BACKEND_URL, {
      method: "POST",
      body: JSON.stringify(payload), // json input object
      headers: {
        "Content-Type": "application/json"
      }
    });
    return await response.json();
  }
}

export default Backend;
