import os
import openai  
import streamlit as st
import csv
import ast
import pandas as pd

os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']

delimiter = "###"

# Streamlit UI
st.title("Process CSV Generator")
st.write("Use this tool to generate any process in detail. Just type in the name and your situation and get a CSV file of processes, inputs and outputs. The generation will take about 3 Minutes.")
st.image('https://i.imgur.com/kNfSHLC.png', caption='Example Output.', use_column_width=True)
process_name = st.text_input("Enter the process name:", "User Research")
company_type = st.text_input("Enter the company type:", "Startup")


def generate_expert_role(process_name):
    # Construct the prompt for the OpenAI API
    prompt = f"Describe an expert role with knowledge about {process_name} for {company_type} in up to 40 words. Write in plain text. Start your reply with 'You are'."
    
    # Call the OpenAI API using the ChatCompletion endpoint
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100  
        )
        
        # Extract the relevant content from the API response
        expert_role = response['choices'][0]['message']['content'].strip()
    except KeyError:
        return "An error occurred while parsing the API response."
    
    print(f"Generated expert role: {expert_role}")

    return expert_role

def generate_phases(process_name, expert_role):
    prompt = f"""{expert_role}. Generate a process for {process_name}. It is made for {company_type}. Map out the 3-5 high level phases of this process. Define Input, Task and Output for each of them in a few bullet points."""
    # Call the OpenAI API using the ChatCompletion endpoint
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000 
        )
        
        # Extract the relevant content from the API response
        phases = response['choices'][0]['message']['content'].strip()
    except KeyError:
        return "An error occurred while parsing the API response."
    
    print(f"Phases: {phases}")

    return phases


def generate_steps(process_name, expert_role, phases, company_type):
    system = f"""{expert_role} You will create an extensive process for {process_name}. It is made for {company_type}. We will go from the existing Phases = Process Level one to process level 2 and level 3 which are the subprocesses of eachother. This is process level 1: {phases}."""
    prompt = f"""You will first generate a list of Process Level 2 with short 1-2 bullet points for input, process level 3 and output. Afterwards you will generate Process Level 3 for each process in process level 2. For each Process level 3 define, input, task and output."""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0
        )
        # Extract the relevant content from the API response
        steps = response['choices'][0]['message']['content'].strip()
    except KeyError:
        return "An error occurred while parsing the API response."
    
    print(f"Steps: {steps}")

    return steps

def generate_library(steps):
    prompt=f"""You will take the content {steps} and output is as a python dictionary.
         The dictionary will be formatted the following way {{
    'ID': {{
        'Process Level 1': 'Level_1_Name',
        'Process Level 2': 'Level_2_Name',
        'Process Level 3': 'Level_3_Name',
        'Input': 'Required_Inputs',
        'Task': 'Tasks_to_Perform',
        'Output': 'Expected_Outputs',
        }}
    }},
    .   
         You will output the full dictionary and every process Level 3 - one per ID. You will not leave out anything. You will only output the dictionary and nothing else."""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0
        )
        # Extract the relevant content from the API response
        library = response['choices'][0]['message']['content'].strip()
    except KeyError:
        return "An error occurred while parsing the API response."
    
    print(f"Library: {library}")
    
    return library

def write_dict_to_csv(dictionary, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['ID', 'Process Level 1', 'Process Level 2', 'Process Level 3', 'Input', 'Task', 'Output']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for id, value in dictionary.items():
            row = {'ID': id}
            row.update(value)
            writer.writerow(row)

def str_to_dict(dict_str):
    """Converts a dictionary string to a dictionary object."""
    try:
        return ast.literal_eval(dict_str)
    except (SyntaxError, ValueError):
        return "Conversion failed"

# Initialize the session state variable if it doesn't exist yet
if 'library_dict' not in st.session_state:
    st.session_state.library_dict = None

# Button to trigger all parts in sequence
if st.button("Generate CSV File"):
    
    # Show a spinner while generating the expert role
    with st.spinner('Generating Expert Role...'):
        expert_role = generate_expert_role(process_name)
    st.success('Expert Role Generated!')
    st.subheader('CSV Generation Process')
    st.write("Generated Expert Role: " + expert_role + "\n" + "---")

    # Show a spinner while generating phases
    with st.spinner('Generating Phases...'):
        phases = generate_phases(process_name, expert_role)
    st.success('Phases Generated!')
    st.write(f"Generated Phases: {phases}  \n---")

    
    # Show a spinner while generating steps
    with st.spinner('Generating Steps...'):
        steps = generate_steps(process_name, expert_role, phases, company_type)
    st.success('Steps Generated!')
    st.write(f"Generated Steps: {steps}  \n---")

    # Show a spinner while generating library
    with st.spinner('Generating Library...'):
        library = generate_library(steps)
    st.session_state.library_dict = str_to_dict(library)  # Store in session state
    
  # Check if there's data in the session state to display
if st.session_state.library_dict is not None:
    if st.session_state.library_dict != "Conversion failed":
        csv_file_name = f"{process_name}_generated.csv"
        write_dict_to_csv(st.session_state.library_dict, csv_file_name)
        
        df = pd.read_csv(csv_file_name)
        st.subheader('Generated CSV Data')
        st.dataframe(df)
        
        st.download_button(
            label="Download Library CSV",
            data=pd.read_csv(csv_file_name).to_csv(index=False),
            file_name="library.csv",
            mime="text/csv"
        )
    else:
        st.error("Failed to convert library string to dictionary.")
