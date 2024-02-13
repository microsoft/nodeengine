# Telemetry Library

`telemetry.py` in the libs library assists with capturing and recording performance and usage metrics within the Node Engine. It is essential for monitoring and improving the engine's components and flows.

## Timer Class

- **Time Tracking**: Provides methods for starting and stopping a timer, and computing the elapsed time, aiding in performance measurement.

## Telemetry Class

- **Initialization**: Requires session ID, flow key, and component key for creating a telemetry storage key.

- **Data Capture**: The `capture` method stores telemetry data, while `capture_value` updates a specific metric, and `capture_average` calculates and updates an average value.

- **Utility Operations**: Supports advanced telemetry capture operations critical for optimizing the Node Engine's performance and debugging component execution.