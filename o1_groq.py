# File path: g1_app_optimized_confirm.py
import streamlit as st
import groq
import os
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Centralized configuration
CONFIG = {
    'GROQ_MODEL': os.getenv('GROQ_MODEL', 'llama-3.1-70b-versatile'),
    'DEFAULT_TEMPERATURE': float(os.getenv('DEFAULT_TEMPERATURE', 0.2)),
    'DEFAULT_MAX_TOKENS': int(os.getenv('DEFAULT_MAX_TOKENS', 300))
}

# Groq client
client = groq.Groq()

# Add caching to avoid redundant API calls
@st.cache_data
def make_api_call(messages, max_tokens, temperature, is_final_answer=False):
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=CONFIG['GROQ_MODEL'],
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            if attempt == 2:
                return {
                    "title": "Error",
                    "content": f"Failed to generate final answer after 3 attempts. Error: {str(e)}" if is_final_answer
                    else f"Failed to generate step after 3 attempts. Error: {str(e)}",
                    "next_action": "final_answer" if not is_final_answer else None
                }
            time.sleep(1)

# Generate the reasoning response in steps
def generate_response(prompt, max_tokens, temperature):
    messages = [
        {"role": "system", "content": """You are an advanced AI reasoning assistant tasked with delivering a comprehensive analysis of a specific problem or question.  Your goal is to outline your reasoning process in a structured and transparent manner, with each step reflecting a thorough examination of the issue at hand, culminating in a well-reasoned conclusion.

### Structure for Each Reasoning Step:
1.  **Title**: Clearly label the phase of reasoning you are currently in.
2.  **Content**: Provide a detailed account of your thought process, explaining your rationale and the steps taken to arrive at your conclusions.
3.  **Next Action**: Decide whether to continue with further reasoning or if you are ready to provide a final answer.

### Response Format:
Please return the results in the following JSON format:
- `title`: A brief label for the current reasoning phase.
- `content`: An in-depth explanation of your reasoning process for this step.
- `next_action`: Choose `'continue'` to proceed with further reasoning or `'final_answer'` to conclude.

### Key Instructions:
1.  Conduct **at least 5 distinct reasoning steps**, each building on the previous one.
2.  **Acknowledge the limitations** inherent to AI, specifically what you can accurately assess and what you may struggle with.
3.  **Adopt multiple reasoning frameworks** to resolve the problem or derive conclusions, such as:
- **Deductive reasoning** (drawing specific conclusions from general principles)
- **Inductive reasoning** (deriving broader generalizations from specific observations)
- **Abductive reasoning** (choosing the best possible explanation for the given evidence)
- **Analogical reasoning** (solving problems through comparisons and analogies)
4.  **Critically analyze your reasoning** to identify potential flaws, biases, or gaps in logic.
5.  When reviewing, apply a **fundamentally different perspective or approach** to enhance your analysis.
6.  **Employ at least 2 distinct reasoning methods** to derive or verify the accuracy of your conclusions.
7.  **Incorporate relevant domain knowledge** and **best practices** where applicable, ensuring your reasoning aligns with established standards.
8.  **Quantify certainty levels** for each step and your final conclusion, where applicable.
9.  Consider potential **edge cases or exceptions** that could impact the outcome of your reasoning.
10.  Provide **clear justifications** for dismissing alternative hypotheses or solutions that arise during your analysis.

### Example JSON Output:

```json
{
"title": "Initial Problem Analysis",
"content": "To approach this problem effectively, I'll first break down the given information into key components.  This involves identifying... [detailed explanation]...  By structuring the problem in this way, we can systematically address each aspect.",
"next_action": "continue"
}
```"""},
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": "Thank you! I will now think step by step..."}
    ]

    steps = []
    step_count = 1
    total_thinking_time = 0

    while True:
        start_time = time.time()
        step_data = make_api_call(messages, max_tokens, temperature)
        thinking_time = time.time() - start_time
        total_thinking_time += thinking_time

        steps.append((f"Step {step_count}: {step_data['title']}", step_data['content'], thinking_time))
        messages.append({"role": "assistant", "content": json.dumps(step_data)})

        if step_data['next_action'] == 'final_answer':
            break
        step_count += 1

    # Final answer step
    final_data = make_api_call(messages, 200, temperature, is_final_answer=True)
    steps.append(("Final Answer", final_data['content'], thinking_time))

    return steps, total_thinking_time

# Main Streamlit app
def main():
    st.set_page_config(page_title="g1 prototype", page_icon="🧠", layout="wide")

    # Sidebar settings
    with st.sidebar:
        st.title("Settings")
        st.markdown("Adjust the parameters below:")
        temperature = st.slider('Temperature', min_value=0.0, max_value=1.0, value=CONFIG['DEFAULT_TEMPERATURE'], key='temperature_slider')
        max_tokens = st.number_input('Max Tokens', min_value=50, max_value=20000, value=CONFIG['DEFAULT_MAX_TOKENS'], key='max_tokens_input')
        st.markdown("---")
        st.markdown("**Current Configuration**")
        st.markdown(f"**Model**: `{CONFIG['GROQ_MODEL']}`")
        st.markdown(f"**Temperature**: `{temperature}`")
        st.markdown(f"**Max Tokens**: `{max_tokens}`")

    st.title("g1: Using Llama-3.1 70b on Groq to create o1-like reasoning chains")

    # Custom CSS for improved UI aesthetics
    st.markdown("""
    <style>
    .stTextInput > div > label {
        font-size: 20px;
        color: #1f77b4;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        padding: 12px 24px;
        font-size: 16px;
        border: none;
        cursor: pointer;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    This is an early prototype of using prompting to create o1-like reasoning chains to improve output accuracy. 
    It is not perfect, and accuracy has yet to be formally evaluated. 
    It is powered by Groq to ensure fast reasoning steps!

    Forked from [bklieger-groq](https://github.com/bklieger-groq)
    Open source [repository here](https://github.com/Ai-trainee/o1-flow)
    """)

    # User query input
    user_query = st.text_input("Enter your query:", placeholder="e.g., How many 'R's are in the word strawberry?")

    # Add a button for confirmation of execution
    if st.button("Run Query"):
        if user_query.strip() == "":
            st.warning("Please enter a valid query.")
        else:
            st.write("Generating response...")

            # Add a loading spinner while generating responses
            with st.spinner('Processing your query...'):
                # Generate and display the response
                steps, total_thinking_time = generate_response(user_query, max_tokens, temperature)

                # Display response with progress
                progress_bar = st.progress(0)
                for idx, (title, content, thinking_time) in enumerate(steps):
                    progress_bar.progress((idx + 1) / len(steps))
                    if title == "Final Answer":
                        st.subheader(f"{title}")
                        st.write(content.replace('\n', '<br>'), unsafe_allow_html=True)
                    else:
                        with st.expander(f"{title} ({thinking_time:.2f}s)", expanded=True):
                            st.write(content.replace('\n', '<br>'), unsafe_allow_html=True)

            # Display total thinking time
            st.success(f"**Total thinking time: {total_thinking_time:.2f} seconds**")

            # Option to download results
            if st.button("Download Results"):
                json_data = json.dumps([{"title": title, "content": content} for title, content, _ in steps], indent=4)
                st.download_button("Download", json_data, file_name="reasoning_results.json", mime="application/json")


if __name__ == "__main__":
    main()
