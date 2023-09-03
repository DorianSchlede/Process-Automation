import os
import openai  
import gradio as gr
import csv
import ast

# Set the OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

process_name = "User Research"
company_type = "Startup"
delimiter = "###"

def str_to_dict(dict_str):
    """Converts a dictionary string to a dictionary object."""
    try:
        return ast.literal_eval(dict_str)
    except (SyntaxError, ValueError):
        return "Conversion failed"

def write_dict_to_csv(dictionary, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['ID', 'Process Level 1', 'Process Level 2', 'Input', 'Task', 'Output']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for id, value in dictionary.items():
            row = {'ID': id}
            row.update(value)
            writer.writerow(row)


def generate_expert_role(process_name):
    # Construct the prompt for the OpenAI API
    prompt = f"Describe an expert role with knowledge about {process_name} for {company_type} in up to 40 words. Start your reply with 'You are'."
    
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
    prompt = f"""{expert_role}. Generate an extensive process for {process_name}. It is made for {company_type}. Map out the 3-5 high level phases of this process. Define Input, Task and Output for each of them."""
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
    system = f"""{expert_role} You will create an extensive process for {process_name}. It is made for {company_type}. We will go two Process Levels deep. This is process level 1: {phases}."""
    prompt = f"""You will now generate the Process Level 2 for each of these and define process level 1, process level 2, input, task and output. Generate 2-5 processes level 2 for each process level 1."""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0
        )
        # Extract the relevant content from the API response
        steps = response['choices'][0]['message']['content'].strip()
    except KeyError:
        return "An error occurred while parsing the API response."
    
    return steps

def generate_library(steps):
    prompt=f"""You will take the content {steps} and output is as a python dictionary.
         The dictionary will be formatted the following way {{
    'ID': {{
        'Process Level 1': 'Level_1_Name',
        'Process Level 2': 'Level_2_Name',
        'Input': 'Required_Inputs',
        'Task': 'Tasks_to_Perform',
        'Output': 'Expected_Outputs',
        }}
    }}.   
         You will only output the dictionary and nothing else."""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0
        )
        # Extract the relevant content from the API response
        library = response['choices'][0]['message']['content'].strip()
    except KeyError:
        return "An error occurred while parsing the API response."
    
    return library

def write_dict_to_csv(library, csv_file_name):
    with open(csv_file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        header = ["ID", "Process Level 1", "Process Level 2", "Input", "Task", "Output"]
        writer.writerow(header)
        for id, value in library.items():
            row = [id]
            for h in header[1:]:
                row.append(value.get(h, ""))
            writer.writerow(row)


# Function to run your script and generate CSV
def run_script(process_name, company_type):
    # Your existing logic here
    expert_role = generate_expert_role(process_name)
    phases = generate_phases(process_name, expert_role)
    steps = generate_steps(process_name, expert_role, phases, company_type)
    library = generate_library(steps)
    
    # Convert the library string to dictionary
    library_dict = str_to_dict(library)
    
    # Define the directory where you want to save the file
    save_directory = "C:\\Users\\Dorian\\OneDrive - BildungsCentrum der Wirtschaft gemeinnützige Gesellschaft mbH\\Code\\Synthetic User Research\\Processes"
    
    # Create the full path to the file
    csv_file_name = "process_data.csv"
    csv_file_path = os.path.join(save_directory, csv_file_name)

    # Write the dictionary to a CSV file
    if library_dict != "Conversion failed":
        write_dict_to_csv(library_dict, csv_file_path)
    else:
        return "Failed to convert library string to dictionary."
        
    # Return the result you want to display in the Gradio interface and the CSV file
    return f"Expert Role: {expert_role}\nPhases: {phases}\nSteps: {steps}", csv_file_path

# Create Gradio interface
demo = gr.Interface(
    fn=run_script,  # the function to wrap
    inputs=["text", "text"],  # the types of input your function needs
    outputs=["text", gr.outputs.File(label="Download CSV")]  # the types of output your function returns
)

demo.launch(share=True)

# Generate an expert role
expert_role = generate_expert_role(process_name)

# Generate Process Level 1
phases = generate_phases(process_name, expert_role)

# Generate Process Level 2
steps = generate_steps(process_name, expert_role, phases, company_type)

# Library
library_str = generate_library(steps)
print(f"Steps Library: {library_str}")

# Convert the string representation of the dictionary to an actual dictionary
library_dict = str_to_dict(library_str)