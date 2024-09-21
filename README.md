

# **o1: Enhancing LLMs with Dynamic Reasoning Chains**

[**Video Demo**](https://github.com/user-attachments/assets/db2a221f-f8eb-48c3-b5a7-8399c6300243)

## **Introduction**

This tutorial introduces **o1**, an experimental method designed to enhance the logical reasoning capabilities of Large Language Models (LLMs) using **dynamic reasoning chains**. By guiding LLMs to "think" step-by-step, o1 allows them to tackle logical problems that often confuse state-of-the-art models. 

Unlike traditional reasoning methods, o1 visualizes every reasoning step, offering a more transparent way to understand how the model arrives at its conclusions. The system supports multiple LLM backends, including local and cloud-based options.

> **Note:** While inspired by OpenAI's advanced reasoning model, this experiment does not aim to replicate or compete with it. Instead, it explores the potential of prompting to guide logical reasoning. 

---

## **Why o1?**

Traditional LLMs often struggle with logic-heavy tasks like counting or complex problem-solving. While OpenAI's **Chain of Thought (CoT)** method addresses this by training LLMs to reason in stages, o1 introduces a dynamic and prompt-driven approach. The key benefits of o1 include:

1. **Step-by-step reasoning**: Each reasoning token is visible to users, providing transparency.
2. **Multiple backends**: o1 can integrate with both cloud-based and local models.
3. **Prompting for improvement**: Through carefully designed prompts, models are guided to explore alternative solutions, improving logical accuracy without retraining.

By leveraging prompt-based techniques, o1 enables existing models to handle problems like the **Strawberry problem** (e.g., "How many Rs are in the word strawberry?"), which many models traditionally fail.

---

## **How Does o1 Work?**

o1 operates on the principle of **dynamic Chain of Thought (CoT)**, where the LLM reasons through a series of intermediate steps before reaching a conclusion. At each step, the model can either proceed with another reasoning step or provide a final answer. Here’s how it works:

1. **Breaking Down the Problem**: The model receives a problem and is prompted to break it into logical components.
2. **Exploring Alternatives**: Prompts encourage the LLM to consider alternative methods for solving the problem (e.g., "use at least 3 different approaches").
3. **Iterative Reasoning**: The model is prompted to question its previous conclusions and explore other angles, improving the accuracy of the final answer.
4. **Dynamic Feedback**: The LLM's reasoning process is dynamically displayed to users, allowing for real-time feedback and adjustments.

In testing, using prompts alone (without model retraining), o1 improved accuracy on the Strawberry problem to **~70%** with **Llama-3.1 70b**, compared to **0%** with default settings and **30%** with ChatGPT-4o.

### **Example of a Prompt Breakdown:**
- **Prompt**: "Use at least 3 methods to find the number of Rs in the word 'strawberry'."
- **Step 1**: Count characters manually.
- **Step 2**: Check the result by comparing against other similar words.
- **Step 3**: Analyze common patterns and mistakes in character counting.

---

## **Supported Models**

1. **Llama-3.1 70b on Groq**: The original implementation utilizes the **Llama-3.1 70b** model hosted on Groq, known for its capability to handle complex reasoning tasks.

2. **Ollama Local Models**: For those preferring to run models locally, o1 supports the **Ollama** environment, allowing the use of various open-source models on personal machines.

---

## **Installation & Setup**

Here’s a step-by-step guide to setting up **o1** with both Streamlit and Gradio interfaces.

### **Quickstart (Streamlit UI on Groq)**

1. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Set environment variable**:
   ```bash
   export GROQ_API_KEY=gsk...
   ```

4. **Run the app**:
   ```bash
   streamlit run o1_groq.py
   ```

### **Quickstart (Gradio UI)**

For those preferring **Gradio**, follow these steps:

1. **Navigate to the Gradio folder**:
   ```bash
   cd gradio
   ```

2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Run the app**:
   ```bash
   python3 o1_groq.py
   ```

### **For Ollama Local Models**

1. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure your `.env` file**:
   Add the following environment variables:
   ```
   OLLAMA_URL=your_ollama_url
   OLLAMA_MODEL=model_name
   ```

4. **Run the app**:
   ```bash
   streamlit run o1_ollama.py
   ```

---

## **Performance & Limitations**

Initial tests show that **o1** significantly improves performance on simple logical tasks, achieving **60-80%** accuracy on problems that typically stump LLMs. However, formal evaluation is still ongoing.

> **Important**: o1 is not intended to be a perfect solution, but rather a tool to demonstrate the power of well-structured prompts in logical reasoning tasks.

### **Example: Is 3307 a Prime Number?**
**Answer**: Yes.  
![img.png](docs/img1.png)

## **Interface Updates**
![img.png](docs/img5.png)

---

## **Video Tutorial**

Watch the step-by-step guide for setting up and using **o1**:

<video width="640" height="360" controls>
  <source src="./docs/tutor.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

### 其他例子在这：文章介绍
https://mp.weixin.qq.com/s/RnDBwEHlGWEo01YROsHvmw

## **Forks**

https://github.com/bklieger-groq/g1

---

## **Conclusion**

**o1** demonstrates how prompting strategies can significantly enhance the reasoning capabilities of LLMs. By breaking down problems into dynamic steps, encouraging alternative solutions, and providing an intuitive interface, **o1** offers a fresh approach to overcoming common LLM challenges.

For developers and researchers interested in LLM reasoning improvement, **o1** provides a practical, accessible tool for experimentation.