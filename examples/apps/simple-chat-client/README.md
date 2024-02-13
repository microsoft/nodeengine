# Simple Chat Client Example App

- Read the top level [README](../../../../README.md) to get an understanding of the overall project and how it works.
- Run the app with `uvicorn examples.apps.simple-chat-client.app:app --reload`
- Open a browser to `http://localhost:8000/?session_id=my-session-1&user_name=User` to see the app running.
  - Change the `session_id` and `user_name` query parameters to values of your own choosing.

## Things to try

- Modify `definitions/agent-response.json` to customize the agent persona.
- Modify `definitions/agent-response.json` and edit the system prompt for the `generate_response` step in the flow.
- Copy the default prompts from `components/generate_response.py` into `definitions/agent-response.json`, as a value in the flow `generate_response` step, and edit them to your liking.

## Development

This project is a proof-of-concept for exploring fast/low-cost app development approaches and utilizes the following technologies:

- [FastAPI](https://fastapi.tiangolo.com/) - A modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.
- [NiceGUI](https://nicegui.io/) - A simple, fast, and lightweight GUI framework for Python, using the web as its display.
  - [Documentation](https://nicegui.io/documentation)
  - [Examples](https://nicegui.io/#examples)
- [Tailwind CSS](https://tailwindcss.com/) - Tailwind CSS works by scanning all of your HTML files, JavaScript components, and any other templates for class names, generating the corresponding styles and then writing them to a static CSS file. It's fast, flexible, and reliable — with zero-runtime.
  - [Documentation](https://tailwindcss.com/docs/utility-first)

Over time, we will develop and standardize on patterns for reusable components to move towards a toolkit for quickly trying out new app experiences.
