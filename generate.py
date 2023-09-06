import os
import openai  
import streamlit as st
import csv
import ast
import pandas as pd

os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']

delimiter = "###"


def call_openai_api(prompt, max_tokens=100, model="gpt-4", temperature=0):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response['choices'][0]['message']['content'].strip()
    except (KeyError, Exception) as e:
        return f"An error occurred: {e}"


def generate_expert_role(process_name, company_type):
    try:
        prompt = f"Describe an expert role with knowledge about {process_name} for {company_type} in up to 40 words. Write in plain text. Start your reply with 'You are'."
        expert_role = call_openai_api(prompt, max_tokens=100, model="gpt-3.5-turbo")
        st.write(f"Generated expert role: {expert_role}")
        return expert_role
    except TypeError as te:
        st.write(f"TypeError: {str(te)}")
    except Exception as e:
        st.write(f"An unexpected error occurred: {str(e)}")

def generate_phases(process_name, expert_role, company_type):
    prompt = f"{expert_role}. Generate a process for {process_name}. It is made for {company_type}. Map out the 3-5 high level phases of this process. Define Input, Task and Output for each of them in a few bullet points."
    phases = call_openai_api(prompt, max_tokens=1000)
    return phases

def generate_steps(process_name, expert_role, phases, company_type):
    prompt = f"""{expert_role} You will create an extensive process for {process_name}. It is made for {company_type}. We will go from the existing Phases = Process Level one to process level 2 and level 3 which are the subprocesses of eachother. This is process level 1: {phases}.
    You will first generate a bullet list of all Processes Level 2. 
    In the following Structure:
    [1. Process Level 1 Name]
    - 1.1: Input, Task, Output
    - 1.1.1: Input, Task, Output
    - 1.1.2: Input, Task, Output
    - 1.1.3:Input, Task, Output
    - 1.2. Input, Task, Output
    - 1.2.1 Input, Task, Output
    - 1.2.2 Input, Task, Output
    - 1.3. Input, Task, Output
    - ...
    [2. Process Level 1 Name]
    - 2.1
    - ...
    Afterwards you will generate a detailled version of process level 3 with one bullet points each for input, task and output. Afterwards you will generate Process Level 3 for each process in process level 2. For each Process level 3 define, input, task and output."""

    steps = call_openai_api(prompt, max_tokens=3000)
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
    
    library = call_openai_api(prompt, max_tokens=4000)
    print(f"Library: {library}")
    return library

def generate_csv_string(dictionary):
    output = io.StringIO()
    fieldnames = ['ID', 'Process Level 1', 'Process Level 2', 'Process Level 3', 'Input', 'Task', 'Output']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for id, value in dictionary.items():
        row = {'ID': id}
        row.update(value)
        writer.writerow(row)
    return output.getvalue()


def str_to_dict(dict_str):
    """Converts a dictionary string to a dictionary object."""
    try:
        return ast.literal_eval(dict_str)
    except (SyntaxError, ValueError):
        return "Conversion failed"


# Streamlit UI
st.title("Process CSV Generator")

# Create session state variable for page if it doesn't exist
if 'page' not in st.session_state:
    st.session_state.page = "Generate Process"

# Sidebar for selection
st.sidebar.markdown("**Menu**")
if st.sidebar.button("Generate Process"):
    st.session_state.page = "Generate Process"
if st.sidebar.button("All Processes"):
    st.session_state.page = "All Processes"

if st.session_state.page == "Generate Process":
    st.write("Use this tool to generate any process in detail. Just type in the name and your situation and get a CSV file of processes, inputs and outputs. The generation will take about 3 Minutes.")
    st.image('https://i.imgur.com/kNfSHLC.png', caption='Example Output.', use_column_width=True)
    process_name = st.text_input("Enter the process name:", "User Research")
    company_type = st.text_input("Enter the company type:", "Startup")

    if st.session_state.library_dict is not None:
        if st.session_state.library_dict != "Conversion failed":
            csv_string = generate_csv_string(st.session_state.library_dict)  # Using the new function here
            df = pd.read_csv(io.StringIO(csv_string))  # Reading the CSV string to DataFrame

            st.subheader('Generated CSV Data')
            st.dataframe(df)

            st.download_button(
                label="Download Library CSV",
                data=csv_string,
                file_name=f"{process_name}_library.csv",
                mime="text/csv"
            )


    # Button to trigger all parts in sequence
    if st.button("Generate CSV File"):
    
        # Show a spinner while generating the expert role
        with st.spinner('Generating Expert Role...'):
            expert_role = generate_expert_role(process_name, company_type)
        st.success('Expert Role Generated!')
        st.subheader('CSV Generation Process')
        st.write("Generated Expert Role: " + expert_role + "\n" + "---")

        # Show a spinner while generating phases
        with st.spinner('Generating Phases...'):
            phases = generate_phases(process_name, expert_role, company_type)
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
        
    if st.session_state.library_dict is not None:
        if st.session_state.library_dict != "Conversion failed":
            csv_string = generate_csv_string(st.session_state.library_dict)
            df = pd.read_csv(io.StringIO(csv_string))

            st.subheader('Generated CSV Data')
            st.dataframe(df)

            st.download_button(
                label="Download Library CSV",
                data=csv_string,
                file_name=f"{process_name}_library.csv",
                mime="text/csv"
            )
        else:
            st.error("Failed to convert library string to dictionary.")




elif st.session_state.page == "All Processes":
    st.write("Debug: Entered All Processes block")  # Debugging line
    # Create directory if it does not exist
    if not os.path.exists('saved_csvs'):
        os.makedirs('saved_csvs')
    saved_csvs = os.listdir('saved_csvs')
    st.write("List of all saved processes:")
    for csv in saved_csvs:
        st.write(csv)
