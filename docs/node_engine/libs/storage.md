# Storage Library

Located in the libs directory, `storage.py` defines the Storage class responsible for managing persistent storage in the Node Engine's execution environment.

## Storage Class

- **File Handling**: Includes methods for getting file names based on session IDs and keys, retrieving data from storage, and setting data within storage files.

- **CRUD Operations**: Provides a full set of create, read, update, and delete operations for managing the contents within the storage system.

- **Listing Files**: The `list` method allows for enumeration of all files associated with a given session ID.

This storage utility is critical for components of the Node Engine that require persistence of data beyond the lifecycle of a single flow execution, providing a means to read from and write to a file-based storage system.