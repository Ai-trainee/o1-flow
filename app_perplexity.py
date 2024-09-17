import streamlit as st
import json
import time
import requests  # Add this import for making HTTP requests to Ollama
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get configuration from .env file
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "llama-3.1-sonar-small-128k-online")

if not PERPLEXITY_API_KEY:
    raise ValueError("PERPLEXITY_API_KEY is not set in the .env file")


def make_api_call(messages, max_tokens, is_final_answer=False):
    for attempt in range(3):
        try:
            url = "https://api.perplexity.ai/chat/completions"

            payload = {"model": PERPLEXITY_MODEL, "messages": messages}
            headers = {
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json",
            }

            print(f"payload: {payload}")

            response = requests.request("POST", url, json=payload, headers=headers)

            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text}")

            response.raise_for_status()
            response_json = response.json()
            content = response_json["choices"][0]["message"]["content"]
            
            # Try to parse the content as JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # If parsing fails, return the content as is
                return {
                    "title": "Raw Response",
                    "content": content,
                    "next_action": "final_answer" if is_final_answer else "continue"
                }

        except requests.exceptions.HTTPError as e:
            if response.status_code == 400:
                error_message = f"400 Bad Request: {response.text}"
                print(error_message)
                if attempt == 2:
                    return {
                        "title": "Error",
                        "content": error_message,
                        "next_action": "final_answer",
                    }
            else:
                # Handle other HTTP errors
                if attempt == 2:
                    error_message = f"HTTP error occurred: {str(e)}"
                    return {
                        "title": "Error",
                        "content": error_message,
                        "next_action": "final_answer",
                    }
        except json.JSONDecodeError:
            if attempt == 2:
                return {
                    "title": "Error",
                    "content": f"Failed to parse API response: {response.text}",
                    "next_action": "final_answer",
                }
        except requests.exceptions.RequestException as e:
            if attempt == 2:
                error_message = f"API request failed after 3 attempts. Error: {str(e)}"
                return {
                    "title": "Error",
                    "content": error_message,
                    "next_action": "final_answer",
                }
        time.sleep(1)  # Wait for 1 second before retrying


def generate_response(prompt):

    messages = [
        {
            "role": "system",
            "content": """You are an expert AI assistant that explains your reasoning step by step. For each step, provide a title that describes what you're doing in that step, along with the content. Decide if you need another step or if you're ready to give the final answer. Respond in JSON format with 'title', 'content', and 'next_action' (either 'continue' or 'final_answer') keys. USE AS MANY REASONING STEPS AS POSSIBLE. AT LEAST 3. BE AWARE OF YOUR LIMITATIONS AS AN LLM AND WHAT YOU CAN AND CANNOT DO. IN YOUR REASONING, INCLUDE EXPLORATION OF ALTERNATIVE ANSWERS. CONSIDER YOU MAY BE WRONG, AND IF YOU ARE WRONG IN YOUR REASONING, WHERE IT WOULD BE. FULLY TEST ALL OTHER POSSIBILITIES. YOU CAN BE WRONG. WHEN YOU SAY YOU ARE RE-EXAMINING, ACTUALLY RE-EXAMINE, AND USE ANOTHER APPROACH TO DO SO. DO NOT JUST SAY YOU ARE RE-EXAMINING. USE AT LEAST 3 METHODS TO DERIVE THE ANSWER. USE BEST PRACTICES.

Example of a valid JSON response:
```json
{
    "title": "Identifying Key Information",
    "content": "To begin solving this problem, we need to carefully examine the given information and identify the crucial elements that will guide our solution process. This involves...",
    "next_action": "continue"
}```
""",
        },
        {"role": "user", "content": prompt},
    ]

    steps = []
    step_count = 1
    total_thinking_time = 0

    while True:
        start_time = time.time()
        step_data = make_api_call(messages, 300)
        end_time = time.time()
        thinking_time = end_time - start_time
        total_thinking_time += thinking_time

        steps.append(
            (
                f"Step {step_count}: {step_data['title']}",
                step_data["content"],
                thinking_time,
            )
        )

        messages.append({"role": "assistant", "content": json.dumps(step_data)})

        if step_data["next_action"] == "final_answer":
            break

        step_count += 1

        # Add a user message to maintain alternation
        messages.append({"role": "user", "content": "Continue with the next step."})

        # Yield after each step for Streamlit to update
        yield steps, None  # We're not yielding the total time until the end

    # Generate final answer
    messages.append(
        {
            "role": "user",
            "content": "Please provide the final answer based on your reasoning above.",
        }
    )

    start_time = time.time()
    final_data = make_api_call(messages, 200, is_final_answer=True)
    end_time = time.time()
    thinking_time = end_time - start_time
    total_thinking_time += thinking_time

    steps.append(("Final Answer", final_data["content"], thinking_time))

    yield steps, total_thinking_time


def main():
    st.set_page_config(page_title="p1 prototype - Perplexity version", page_icon="🧠", layout="wide")

    st.title("ol1: Using Perplexity AI to create o1-like reasoning chains")

    st.markdown(
        """
    This is an early prototype of using prompting to create o1-like reasoning chains to improve output accuracy. It is not perfect and accuracy has yet to be formally evaluated. It is powered by Perplexity AI API!
                
    Forked from [bklieger-groq](https://github.com/bklieger-groq)
    Open source [repository here](https://github.com/tcsenpai/ol1-p1)
    """
    )

    st.markdown(f"**Current Configuration:**")
    st.markdown(f"- Perplexity AI Model: `{PERPLEXITY_MODEL}`")

    # Text input for user query
    user_query = st.text_input(
        "Enter your query:",
        placeholder="e.g., How many 'R's are in the word strawberry?",
    )

    if user_query:
        st.write("Generating response...")

        # Create empty elements to hold the generated text and total time
        response_container = st.empty()
        time_container = st.empty()

        # Generate and display the response
        for steps, total_thinking_time in generate_response(user_query):
            with response_container.container():
                for i, (title, content, thinking_time) in enumerate(steps):
                    if title.startswith("Final Answer"):
                        st.markdown(f"### {title}")
                        st.markdown(
                            content.replace("\n", "<br>"), unsafe_allow_html=True
                        )
                    else:
                        with st.expander(title, expanded=True):
                            st.markdown(
                                content.replace("\n", "<br>"), unsafe_allow_html=True
                            )

            # Only show total time when it's available at the end
            if total_thinking_time is not None:
                time_container.markdown(
                    f"**Total thinking time: {total_thinking_time:.2f} seconds**"
                )


if __name__ == "__main__":
    main()
