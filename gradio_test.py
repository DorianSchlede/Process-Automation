import os
import openai  
import gradio as gr

# Create Gradio interface
demo = gr.Interface(
    fn=run_script,  # the function to wrap
    inputs=["text", "text"],  # the types of input your function needs
    outputs=["text", gr.outputs.File(label="Download CSV")]  # the types of output your function returns
)