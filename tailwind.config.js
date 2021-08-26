module.exports = {
  purge: [
    // Keep CSS classes defined in our JS and HTML
    "./assets/**/*",
    "./karspexet/**/*",
  ],
  corePlugins: {
    transform: false,
    // Borders
    ringOffsetColor: false,
    ringOffsetWidth: false,
    ringOpacity: false,
    ringWidth: false,
    ringColor: false,
    // Opacity
    backgroundOpacity: false,
    textOpacity: false,
    opacity: false,
    // Filters
    filter: false,
    grayscale: false,
    hueRotate: false,
    invert: false,
    saturate: false,
    sepia: false,
  },
};
