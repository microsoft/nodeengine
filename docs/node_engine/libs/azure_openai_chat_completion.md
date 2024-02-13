# Azure OpenAI Chat Completion Library

This library file, `azure_openai_chat_completion.py`, provides the functionality to interact with Azure's OpenAI Chat Completion API. It defines a class that handles the creation of chat completions using the OpenAI service.

## AzureOpenAIChatCompletion Class

- **Initialization**: The class does not require explicit initialization and contains an asynchronous `create` method.

- **Create Method**: The `create` method sends messages to the OpenAI API and retrieves chat completions. It accepts parameters for the messages, Azure OpenAI environment variables, and optional parameters like `max_retries` and `retry_delay_ms` for handling API request attempts.

- **Error Handling**: If the API request fails, it will retry based on the provided parameters. Upon exhausting the retries or encountering other exceptions, it will raise an exception with a descriptive error message.

- **Response Processing**: On successful response retrieval, it processes the chat completion and ensures that a valid message is returned based on the completion's `finish_reason`.

This library is essential for facilitating conversational interactions through the Azure OpenAI API and is especially useful when building complex conversation flows within the Node Engine.