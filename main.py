import subprocess
import ollama
import sys

SHELLSP_MODEL = "qwen2.5-coder" 
SHELLSP_SYSPROMPT = 'You are a windows shell expert assistant.'
SHELLSP_NUM_CONTEXT = 32000

model_options = {
    "temperature": 0,
    "num_ctx": SHELLSP_NUM_CONTEXT,
}

model_tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_cmd",
            "description": "Execute a cmd command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to be executed",
                    },
                },
                "required": ["command"],
            },
        },
    },
]

def bash(command):
    try:
        return subprocess.check_output(command, text=True, shell=True)
    except subprocess.CalledProcessError as e:
        return str(e)

def run(model, prompt):
    sys_info = subprocess.check_output("systeminfo", text=True, shell=True).replace("\t", " ").replace("\n", ". ")
    sys_prompt = SHELLSP_SYSPROMPT + " " + sys_info

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": prompt},
    ]

    response = ollama.chat(
        model=model,
        messages=messages,
        options=model_options,
        tools=model_tools
    )

    if 'message' in response:
        print(response['message']['content'])

        if 'tool_calls' in response['message']:
            for tool in response['message']['tool_calls']:
                if tool['function']['name'] == 'execute_cmd':
                    command = tool['function']['arguments']['command']
                    result = bash(command)
                    print(f"Command executed: {result}")
    else:
        print("Error: No 'message' in the response.")

def main():
    if len(sys.argv) < 2:
        print("Por favor, pasa un comando o consulta al prompt.")
        return

    prompt = " ".join(sys.argv[1:])
    run(SHELLSP_MODEL, prompt)

if __name__ == "__main__":
    main()
