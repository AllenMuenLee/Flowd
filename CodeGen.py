import os
import json
import boto3
import ast
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

print(os.getenv("AWS_SECRET_ACCESS_KEY"))

client = OpenAI(
    api_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    base_url="https://api.nova.amazon.com/v1"
)

class CodingAgent:
    def __init__(self):
        self.project_skeletons = {} # Stores code signatures for quota saving

    def get_skeleton(self, code):
        """Saves quota by sending only function/class headers to the AI."""
        try:
            tree = ast.parse(code)
            skeleton = [l.strip() + " ..." for l in code.splitlines() 
                        if any(l.strip().startswith(kw) for kw in ["def ", "class "])]
            return "\n".join(skeleton)
        except: return "# (Code summary)"

    def call_nova(self, data):
        context = "\n".join([f"File {f}:\n{s}" for f, s in self.project_skeletons.items()])
        SYSTEM_PROMPT = """You are a senior software architect and coding agent. the user will give you a description of a coding task, which is a step in a larger project.
        RULES:
        1. Provide ONLY the code. No conversational filler or explanations.
        2. If anything is unclear, like if you can't determine the content of a file from the description, or need to know more about the previous code, please write in the following format:
        ### QUESTION: [Your question here]
        3. for each file of code you want to write, give the format of:
        [File Name.py]
        [Code]
        """
        prompt = f"""
        CONTEXT OF EXISTING FILES:
        {context}

        TASK: {data['description']}
        FILES TO GENERATE: {data['filenames']}

        Please give raw code output below
        """
        response = client.chat.completions.create(
            model="nova-2-lite-v1",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            temperature=0.1,
            max_tokens=3000,
            stream=False
        )
        
        return response.choices[0].message.content


    def run_procedure(self, procedure, visited_nodes = []):
        """Iterates through the dictionary structure: {ID: {data}}"""
        for step_id, data in procedure.items():
            if (step_id in visited_nodes):
                continue
            visited_nodes.append(step_id)
            print(f"--- Executing Step {step_id}: {data['description']} ---")
            
            # Build context from previously created file skeletons
            
            raw_code = self.call_nova(data)
            self.save_and_update(data["filenames"][0], raw_code)

            # If this node has children (as IDs), you would handle them here
            # In your format, 'children' is a list of keys to other dict entries
            if data.get("children"):
                # Filter the main dict for only these children and recurse
                child_subdict = {c_id: procedure[c_id] for c_id in data["children"] if c_id in procedure}
                self.run_procedure(child_subdict)

    def save_and_update(self, file_path, text):
        pattern = r"\[([^\]]+)\]:?\s*```python\n(.*?)\n```"
        
        # re.DOTALL allows the '.' to match newlines within the code block
        matches = re.findall(pattern, text, re.DOTALL)
        print("text:", text)
        print(matches)
        
        extracted_data = {}
        for filename, code in matches:
            extracted_data[filename] = code.strip()

            with open(filename, "w") as f:
                print(code)
                f.write(code)
            
            self.project_skeletons[filename] = self.get_skeleton(code)
            print(f"   [File Saved] {file_path}")

        

# --- YOUR DATA STRUCTURE ---
procedure = {
    "1": {
        "description": "Create a basic Flask API with a health check route.", 
        "filenames": ["app.py"],
        "children": ["2"]
    },
    "2": {
        "description": "Add a /status route that returns JSON {'status': 'ok'}.",
        "filenames": ["app.py"],
        "children": []
    }
}

if __name__ == "__main__":
    agent = CodingAgent()
    agent.run_procedure(procedure)