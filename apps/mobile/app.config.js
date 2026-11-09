/* global __dirname */
const fs = require("node:fs");
const path = require("node:path");

module.exports = ({ config }) => {
  // Build-time gate, before Expo Router discovers routes. Never ship a generated QA tree.
  if (
    fs.existsSync(path.join(__dirname, "app", "dev")) &&
    !(process.env.SEWSURE_QA_ROUTES === "1" && process.env.NODE_ENV === "development")
  ) {
    throw new Error("QA routes present: run npm run qa:remove before normal or production builds.");
  }
  return config;
};
