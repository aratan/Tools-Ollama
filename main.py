import subprocess
import ollama
import sys

# Constantes de configuración
MODEL_NAME = " qwen2.5-coder"  # Nombre del modelo
SYSTEM_PROMPT = 'You are a windows shell expert assistant.'  # Descripción del rol del asistente
NUM_CONTEXT = 32000  # Número de contexto para el modelo

# Opciones para el modelo
model_options = {
    "temperature": 0,
    "num_ctx": NUM_CONTEXT,
}

# Herramientas del modelo
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
    # Obtiene información del sistema
    sys_info = subprocess.check_output("systeminfo", text=True, shell=True).replace("\t", " ").replace("\n", ". ")
    sys_prompt = SYSTEM_PROMPT + " " + sys_info

    # Mensajes para el modelo
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": prompt},
    ]

    # Consulta al modelo
    response = ollama.chat(
        model=model,
        messages=messages,
        options=model_options,
        tools=model_tools
    )

    if 'message' in response:
        print(response['message']['content'])

        # Si hay llamadas a herramientas, se ejecutan
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
    run(MODEL_NAME, prompt)

if __name__ == "__main__":
    main()
