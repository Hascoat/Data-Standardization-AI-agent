#%%

# openai_sdk_agent.py

import time
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# 1. Define the tool schema the assistant can call
tool_schema = [
    {
        "type": "function",
        "function": {
            "name": "map_columns",
            "description": "Maps raw column names to the standardized schema used for transaction normalization.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of raw column names from the original file"
                    }
                },
                "required": ["column_names"]
            }
        }
    }
]

# 2. Load API credentials and initialize client
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 3. Create or retrieve the OpenAI SDK assistant
def get_or_create_assistant():
    assistants = client.beta.assistants.list().data
    for a in assistants:
        if a.name == "Normalization Agent":
            return a

    return client.beta.assistants.create(
        name="Normalization Agent",
        instructions=(
            "You are a data normalization assistant. "
            "You are given a list of raw column names and your job is to match them to this schema: "
            "'contrat_id', 'montant', 'date_operation', 'description'. "
            "Always use the tool `map_columns` to return the mapping. "
            "Do not guess or write the mapping manually — always invoke the tool."
        ),
        model="gpt-4-1106-preview",
        tools=tool_schema
    )

assistant = get_or_create_assistant()

# 4. Local implementation of the tool callable by the assistant
def map_columns_tool(column_names):
    def normalize(col):
        return col.encode("utf-8", errors="ignore").decode("utf-8").lower()

    mapping = {}
    for col in column_names:
        norm = normalize(col)
        print(f"🔍 Inspecting column: {col} → {norm}")
        if any(x in norm for x in ["contrat", "contract", "ref"]) and "contrat_id" not in mapping:
            mapping["contrat_id"] = col
        elif any(x in norm for x in ["montant", "amount", "price", "total"]) and "montant" not in mapping:
            mapping["montant"] = col

        elif "date" in norm and "date_operation" not in mapping:
            mapping["date_operation"] = col
        elif any(x in norm for x in ["libell", "description"]) and "description" not in mapping:
            mapping["description"] = col

    print("🛠️ Final mapping returned by tool:", mapping)
    return mapping

# 5. Run the assistant and submit tool responses
def get_column_mapping(column_names):
    def clean_column(col):
        try:
            return col.encode("latin1", errors="ignore").decode("utf-8", errors="ignore")
        except Exception:
            return col

    # Map cleaned <-> original names
    original_to_cleaned = {col: clean_column(col) for col in column_names}
    cleaned_to_original = {v: k for k, v in original_to_cleaned.items()}
    cleaned_names = list(cleaned_to_original.keys())
    print("🔠 Cleaned column names:", cleaned_names)

    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Please map the following column names to the normalized schema: {cleaned_names}"
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    tool_outputs = []
    start_time = time.time()
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        print("🔁 Assistant run status:", run_status.status)

        if run_status.status == "completed":
            break
        elif run_status.status == "requires_action":
            tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
            print("🛠️ Tool calls:", tool_calls)
            for call in tool_calls:
                if call.function.name == "map_columns":
                    args = json.loads(call.function.arguments)
                    output = map_columns_tool(**args)
                    print("🧪 Tool output to be sent:", output)
                    tool_outputs.append({
                        "tool_call_id": call.id,
                        "output": json.dumps(output)
                    })
            client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
        elif run_status.status in ["failed", "cancelled", "expired"]:
            raise RuntimeError("Assistant run failed: " + run_status.status)

        if time.time() - start_time > 60:
            raise TimeoutError("Assistant run timed out.")
        time.sleep(2)

    if tool_outputs:
        try:
            raw = json.loads(tool_outputs[0]["output"])
            mapping = {k: bytes(v, "utf-8").decode("unicode_escape") for k, v in raw.items()}
            mapped = {k: cleaned_to_original.get(v, v) for k, v in mapping.items()}
            print("✅ Decoded mapping:", mapping)
            print("🔁 Remapped to original column names:", mapped)
            return mapped
        except Exception as e:
            print("⚠️ Failed parsing tool output:", e)
            return {}

    # Fallback: try to parse from assistant message
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print("📩 Raw assistant messages:")
    for msg in messages.data:
        print(msg.role, ":", msg.content[0].text.value if msg.content else "[no content]")
        if msg.role == "assistant":
            try:
                raw_text = msg.content[0].text.value
                response = json.loads(raw_text.replace("'", '"'))
                valid_keys = {"contrat_id", "montant", "date_operation", "description"}
                return {k: cleaned_to_original.get(v, v) for k, v in response.items() if k in valid_keys}
            except Exception as e:
                print("❌ Fallback parsing from assistant message failed:", e)

    print("❌ No valid mapping found.")
    return {}


# %%
