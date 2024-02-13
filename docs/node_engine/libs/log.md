# Logging Library

The `log.py` file offers logging utilities specifically tailored for the Node Engine. It includes custom log levels, loggers, and handlers that integrate with the Node Engine's structure and functionalities.

## LogLevel Class

An enumeration defining custom log levels such as DEBUG, INFO, WARNING, ERROR, and CRITICAL.

## Log Class

- **Initialization**: Custom logger accepting a namespace, FlowDefinition, and log level.

- **Handlers**: Incorporates handlers like `StatusLoggerHandler` and `SSELoggerHandler` which provide status logging and server-sent events emission capacities.

- **Convenience Method**: An invocable instance that defaults to logging information level messages.

- **Utility Functions**: Include `get_log_level` for converting string representations to log level values.

The custom logging solutions here are integral for the Node Engine's monitoring, diagnostics, and interactive feedback mechanisms through standard logging and real-time SSE streams.