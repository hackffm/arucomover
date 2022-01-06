module.exports = {
    uiPort: process.env.PORT || 9010,
    mqttReconnectTime: 15000,
    serialReconnectTime: 15000,
    debugMaxLength: 1000,
    flowFile: 'flows_arucomover.json',
    flowFilePretty: true,
    functionGlobalContext: {
    },

    logging: {
        console: {
            level: "info",
            metrics: false,
            audit: false
        }
    }
}
