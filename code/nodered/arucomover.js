module.exports = {
    uiPort: process.env.PORT || 9010,
    mqttReconnectTime: 15000,
    serialReconnectTime: 15000,
    debugMaxLength: 1000,
    flowFile: 'flows_mmMover2020_03.json',
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
