export default [
  {
    label: "Schließung Bildungseinrichtungen / Kitas",
    summary: "",
    apply: function(beta, beta_slider) {
      return beta * (1 - ((1 - 0.82) / 100) * 100);
    },
    slider: false
  },
  {
    label: "Beschränkung Einzelhandel",
    summary: "",
    apply: function(beta, beta_slider) {
      return beta * (1 - ((1 - 0.91) / 100) * 100);
    },
    slider: false
  },
  {
    label: "Ausgangssperre",
    summary: "",
    apply: function(beta, beta_slider) {
      return beta * (1 - ((1 - 0.27) / 100) * beta_slider);
    },
    slider: true
  },
  {
    label: "Social Distancing",
    summary: "Kneipen, Abendprogramm, Kultur, Sport",
    apply: function(beta, beta_slider) {
      return beta * (1 - ((1 - 0.51) / 100) * beta_slider);
    },
    slider: true
  },
  {
    label: "Beschränkung Restaurants",
    summary: "",
    apply: function(beta, beta_slider) {
      return beta * (1 - ((1 - 0.98) / 100) * 100);
    },
    slider: false
  },
  {
    label: "Veranstaltungsverbot",
    summary: "",
    apply: function(beta, beta_slider) {
      return beta * (1 - ((1 - 0.95) / 100) * beta_slider);
    },
    slider: true
  },
  {
    label: "Isolation von Kranken",
    summary: "",
    apply: function(beta, beta_slider) {
      return beta * (1 - ((1 - 0.82) / 100) * beta_slider);
    }, // TODO
    slider: true
  },
  {
    label: "Grenzbeschränkung",
    summary: "",
    apply: function(beta, beta_slider) {
      return beta * (1 - ((1 - 0.82) / 100) * beta_slider);
    }, // TODO
    slider: true
  }
];
