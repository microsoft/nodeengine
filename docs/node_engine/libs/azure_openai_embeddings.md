# Azure OpenAI Embeddings Library

The `azure_openai_embeddings.py` library file is designed to work with Azure's OpenAI embeddings service. It provides a class that facilitates the creation of embeddings which can be used to measure similarity or perform other natural language processing tasks.

## AzureOpenAIEmbeddings Class

- **Initialization**: No explicit initialization required, but an asynchronous `create` method must be used.

- **Create Method**: Asynchronously communicates with Azure OpenAI to generate embeddings from input text. It supports a list of strings or a single string as input, environment variables for Azure OpenAI, and optional `max_retries` and `retry_delay_ms` for managing API request retries.

- **Error Handling**: Implements retry logic in case of APIConnectionError. Raises exceptions with clear messages upon failure to create embeddings or exhaustion of retries.

- **Response Processing**: Parses the response from Azure OpenAI and extracts the embeddings data for further use in the Node Engine environment.

This library is an essential tool for utilizing OpenAI embeddings within the Node Engine, offering semantic understanding capabilities critical for advanced natural language processing flows.