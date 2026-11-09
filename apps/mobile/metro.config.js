const path = require("path");
const { getDefaultConfig } = require("expo/metro-config");

const config = getDefaultConfig(__dirname);
// The cut guide screens read fixtures from packages/contracts until the API client lands.
config.watchFolders = [...(config.watchFolders ?? []), path.resolve(__dirname, "../../packages/contracts")];
module.exports = config;
