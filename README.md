# o1: Using LLMs to create o1-like reasoning chains

[Video Demo](https://github.com/user-attachments/assets/db2a221f-f8eb-48c3-b5a7-8399c6300243)

This is an early prototype of using prompting strategies to improve LLM reasoning capabilities through o1-like reasoning chains. This allows the LLM to "think" and solve logical problems that usually otherwise stump leading models. Unlike o1, all the reasoning tokens are shown, and the app supports multiple LLM backends.

o1 is experimental and being open sourced to help inspire the open source community to develop new strategies to produce o1-like reasoning. This experiment helps show the power of prompting reasoning in visualized steps, not a comparison to or full replication of o1, which uses different techniques. OpenAI's o1 is instead trained with large-scale reinforcement learning to reason using Chain of Thought, achieving state-of-the-art performance on complex PhD-level problems. 

o1 demonstrates the potential of prompting alone to overcome straightforward LLM logic issues like the Strawberry problem, allowing existing models to benefit from dynamic reasoning chains and an improved interface for exploring them.

## Supported Models

### Llama-3.1 70b on Groq

The original implementation uses Llama-3.1 70b hosted on Groq to create reasoning chains.


### Ollama Local Models

For users who prefer to run models locally, this version also supports Ollama, enabling the use of various open-source models on your local machine.

## How it works

o1 creates reasoning chains, in principle a dynamic Chain of Thought, that allows the LLM to "think" and solve some logical problems that usually otherwise stump leading models.

At each step, the LLM can choose to continue to another reasoning step, or provide a final answer. Each step is titled and visible to the user. The system prompt also includes tips for the LLM. There is a full explanation under Prompt Breakdown, but a few examples are asking the model to "include exploration of alternative answers" and "use at least 3 methods to derive the answer".

The reasoning ability of the LLM is therefore improved through combining Chain-of-Thought with the requirement to try multiple methods, explore alternative answers, question previous draft solutions, and consider the LLM's limitations. This alone, without any training, is sufficient to achieve ~70% accuracy on the Strawberry problem (n=10, "How many Rs are in strawberry?"). Without prompting, Llama-3.1-70b had 0% accuracy and ChatGPT-4o had 30% accuracy.

## Examples

> [!IMPORTANT]
> o1 is not perfect, but it can perform significantly better than LLMs out-of-the-box. From initial testing, o1 accurately solves simple logic problems 60-80% of the time that usually stump LLMs. However, accuracy has yet to be formally evaluated. See examples below.

[Examples section remains unchanged]

## Quickstart

To use the Streamlit UI, follow these instructions:

~~~
python3 -m venv venv
~~~

~~~
source venv/bin/activate
~~~

~~~
pip3 install -r requirements.txt
~~~

~~~
export GROQ_API_KEY=gsk...
~~~

~~~
streamlit run o1-groq.py
~~~

---

Alternatively, follow these additional instructions to use the Gradio UI:

~~~
cd gradio
~~~

~~~
pip3 install -r requirements.txt
~~~

~~~
python3 o1_groq.py
~~~


### For Ollama Local Models

To use the Streamlit UI with Ollama local models, follow these instructions:

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
# Set up your .env file with OLLAMA_URL and OLLAMA_MODEL
streamlit run o1_ollama.py
```
### 例子

#### 3307是质数吗？（答案：是的）
![img.png](examples/img1.png)
### 其他例子在这：文章介绍
https://mp.weixin.qq.com/s/RnDBwEHlGWEo01YROsHvmw

### Forks
https://github.com/bklieger-groq/g1