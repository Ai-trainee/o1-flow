import gradio as gr
import groq
import os
import json
import time


def make_api_call(client, messages, max_tokens, is_final_answer=False):
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            if attempt == 2:
                if is_final_answer:
                    return {"title": "Error", "content": f"Failed to generate final answer after 3 attempts. Error: {str(e)}"}
                else:
                    return {"title": "Error", "content": f"Failed to generate step after 3 attempts. Error: {str(e)}", "next_action": "final_answer"}
            time.sleep(1)  # Wait for 1 second before retrying

def generate_response(client, prompt):
    messages = [
        {"role": "system", "content": """You are an expert AI assistant that explains your reasoning step by step. For each step, provide a title that describes what you're doing in that step, along with the content. Decide if you need another step or if you're ready to give the final answer. Respond in JSON format with 'title', 'content', and 'next_action' (either 'continue' or 'final_answer') keys. USE AS MANY REASONING STEPS AS POSSIBLE. AT LEAST 3. BE AWARE OF YOUR LIMITATIONS AS AN LLM AND WHAT YOU CAN AND CANNOT DO. IN YOUR REASONING, INCLUDE EXPLORATION OF ALTERNATIVE ANSWERS. CONSIDER YOU MAY BE WRONG, AND IF YOU ARE WRONG IN YOUR REASONING, WHERE IT WOULD BE. FULLY TEST ALL OTHER POSSIBILITIES. YOU CAN BE WRONG. WHEN YOU SAY YOU ARE RE-EXAMINING, ACTUALLY RE-EXAMINE, AND USE ANOTHER APPROACH TO DO SO. DO NOT JUST SAY YOU ARE RE-EXAMINING. USE AT LEAST 3 METHODS TO DERIVE THE ANSWER. USE BEST PRACTICES.

Example of a valid JSON response:
```json
{
    "title": "Identifying Key Information",
    "content": "To begin solving this problem, we need to carefully examine the given information and identify the crucial elements that will guide our solution process. This involves...",
    "next_action": "continue"
}```
""" },
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": "Thank you! I will now think step by step following my instructions, starting at the beginning after decomposing the problem."}
    ]
    
    steps = []
    step_count = 1
    total_thinking_time = 0
    
    while True:
        start_time = time.time()
        step_data = make_api_call(client, messages, 300)
        end_time = time.time()
        thinking_time = end_time - start_time
        total_thinking_time += thinking_time
        
        # Handle potential errors
        if step_data.get('title') == "Error":
            steps.append((f"Step {step_count}: {step_data.get('title')}", step_data.get('content'), thinking_time))
            break
        
        step_title = f"Step {step_count}: {step_data.get('title', 'No Title')}"
        step_content = step_data.get('content', 'No Content')
        steps.append((step_title, step_content, thinking_time))
        
        messages.append({"role": "assistant", "content": json.dumps(step_data)})
        
        if step_data.get('next_action') == 'final_answer':
            break
        
        step_count += 1

    # Generate final answer
    messages.append({"role": "user", "content": "Please provide the final answer based on your reasoning above."})
    
    start_time = time.time()
    final_data = make_api_call(client, messages, 200, is_final_answer=True)
    end_time = time.time()
    thinking_time = end_time - start_time
    total_thinking_time += thinking_time
    
    if final_data.get('title') == "Error":
        steps.append(("Final Answer", final_data.get('content'), thinking_time))
    else:
        steps.append(("Final Answer", final_data.get('content', 'No Content'), thinking_time))
    
    return steps, total_thinking_time

def format_steps(steps, total_time):
    html_content = ""
    for title, content, thinking_time in steps:
        if title == "Final Answer":
            html_content += "<h3>{}</h3>".format(title)
            html_content += "<p>{}</p>".format(content.replace('\n', '<br>'))
        else:
            html_content += """
            <details>
                <summary><strong>{}</strong></summary>
                <p>{}</p>
                <p><em>Thinking time for this step: {:.2f} seconds</em></p>
            </details>
            <br>
            """.format(title, content.replace('\n', '<br>'), thinking_time)
    html_content += "<strong>Total thinking time: {:.2f} seconds</strong>".format(total_time)
    return html_content

def main(api_key, user_query):
    if not api_key:
        return "Please enter your Groq API key to proceed.", ""
    
    if not user_query:
        return "Please enter a query to get started.", ""
    
    try:
        # Initialize the Groq client with the provided API key
        client = groq.Groq(api_key=api_key)
    except Exception as e:
        return f"Failed to initialize Groq client. Error: {str(e)}", ""
    
    try:
        steps, total_time = generate_response(client, user_query)
        formatted_steps = format_steps(steps, total_time)
    except Exception as e:
        return f"An error occurred during processing. Error: {str(e)}", ""
    
    return formatted_steps, ""

# Define the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# 🧠 g1: Using Llama-3.1 70b on Groq to Create O1-like Reasoning Chains")
    
    gr.Markdown("""
    This is an early prototype of using prompting to create O1-like reasoning chains to improve output accuracy. It is not perfect and accuracy has yet to be formally evaluated. It is powered by Groq so that the reasoning step is fast!
    
    Open source [repository here](https://github.com/bklieger-groq)
    """)
    
    with gr.Row():
        with gr.Column():
            api_input = gr.Textbox(
                label="Enter your Groq API Key:",
                placeholder="Your Groq API Key",
                type="password"
            )
            user_input = gr.Textbox(
                label="Enter your query:",
                placeholder="e.g., How many 'R's are in the word strawberry?",
                lines=2
            )
            submit_btn = gr.Button("Generate Response")
    
    with gr.Row():
        with gr.Column():
            output_html = gr.HTML()
    
    submit_btn.click(fn=main, inputs=[api_input, user_input], outputs=output_html)

# Launch the Gradio app
if __name__ == "__main__":
    demo.launch()

    ##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