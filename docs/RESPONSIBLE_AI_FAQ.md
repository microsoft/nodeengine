# Node Engine's Responsible AI FAQ 

## What is Node Engine? 

* Node Engine service is a web service that executes a computational flow.
* Each call to the web service can provide a flow definition, dynamically adapting the service to the needs of the caller to facilitate experimentation and multiple simultaneous users with different definitions.
* A client library is provided to simplify calling the service from other Python code.

## What is flow, component, and event?

In our approach, we define computations as a sequence of steps to be executed to complete a given task within a given application.

* A flow is a sequence of components that are executed, starting with a trigger component that has the key value "start"

* A component is a Python class that implements an "execute" method accepting in input configuration, current context and sequence of steps. The method returns updated information and details about how to proceed into the next step.

* Events consist of information exchanged outside the sequence flow, such as information sent to connected clients using SSE (server-side-events).

## What is/are Node Engine’s intended use(s)? 

* Node Engine is designed for rapid experimentation and development of new components and computational flows, e.g. used as a chatbot service in a larger system.

## How was Node Engine evaluated? What metrics are used to measure performance? 

* Node Engine framework has been built from the ground up specifically for the experimentation use-case for our team and next areas of investment. Other frameworks have their own idiosyncrasies that work well for their use-cases, but don't allow us to run as fast as we can with this approach and the ability for us to quickly extend it to meet our not-yet-discovered needs. 

## What are the limitations of Node Engine? How can users minimize the impact of Node Engine’s limitations when using the system? 

* In the context of utilizing AI models, it is essential to be aware that the possibilities of generating harmful, inaccurate, or biased outcomes persist, regardless of the specific AI system being employed. In this case, using Node Engine does not offer any extra advantages or pose any additional risks concerning responsible AI concerns.

* However, developers using Node Engine can adopt a user-centric approach in designing applications, ensuring that users are well-informed and have the ability to approve any actions taken by the AI.

* Additionally, developers should implement mechanisms to monitor and filter any automatically generated information, if deemed necessary.

* By addressing responsible AI issues in this manner, developers can create applications that are not only efficient and useful but also adhere to ethical guidelines and prioritize user trust and safety.

## What operational factors and settings allow for effective and responsible use of Node Engine? 

* First and foremost, developers using Node Engine can precisely define user interactions and how user data is managed. 

* In a sequence of components, additional risks/failures may arise when using non-deterministic behavior. To mitigate this, users can:
  - Implement safety measures and bounds on each component to prevent undesired outcomes.
  - Add output to the user to maintain control and awareness of the system's state.
  - In multi-agent scenarios, build in places that prompt the user for a response, ensuring user involvement and reducing the likelihood of undesired results due to multi-agent looping.

* When working with AI, the developer can enable content moderation in the AI platforms used, and has complete control on the prompts being used, including the ability to define responsible boundaries and guidelines. For instance:

  - When using Azure OpenAI, by default the service includes a content filtering system that works alongside core models. This system works by running both the prompt and completion through an ensemble of classification models aimed at detecting and preventing the output of harmful content. In addition to the content filtering system, the Azure OpenAI Service performs monitoring to detect content and/or behaviors that suggest use of the service in a manner that might violate applicable product terms. The filter configuration can be adjusted, for example to block also "low severity level" content. See [here](https://learn.microsoft.com/azure/ai-services/openai/concepts/content-filter) for more information.

  - The developer can integrate Azure AI Content Safety to detect harmful user-generated and AI-generated content, including text and images. The service includes an interactive Studio online tool with templates and customized workflows. See [here](https://learn.microsoft.com/azure/ai-services/content-safety) for more information.

  - When using OpenAI the developer can integrate OpenAI Moderation to identify problematic content and take action, for instance by filtering it. See [here](https://platform.openai.com/docs/guides/moderation) for more information.
  
  - Other AI providers provide content moderation and moderation APIs, which developers can integrate with Node Engine.
