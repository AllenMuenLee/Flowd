from openai import OpenAI
from dotenv import load_dotenv
import SymbolExt

load_dotenv()

client = OpenAI(
    api_key=os.getenv("NOVA_API_KEY"),
    base_url="https://api.nova.amazon.com/v1"
)

class debugger:
    def __init__(self, project_name):
        self.project_name = project_name
        self.error_files = {}

    def extract_error_nova(self, error_message):
        SYSTEM_PROMPT = "You are a debugger extracter, and your job is to extract the functions and files mentioned in the error message, and return in the given format."
        prompt = f"""
        The error message is:
        {error_message}

        Analyze this error message and extract the following information:
        1. The file path where the error occurred.
        2. The line number of the error.

        return in this format:
        filename - #line number
        ...
        """

        response = client.chat.completions.create(
            model="nova-pro-v1",
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
            max_tokens=2000,
            stream=False
        )

        return response.choices[0].message.content

    def parse_error_files(self, ai_response):
        for line in ai_response.splitlines():
            if ' - #' in line:
                parts = line.split(' - #')
                if len(parts) == 2:
                    filename = parts[0].strip()
                    line_number = parts[1].strip()
                    if filename not in self.error_files:
                        self.error_files[filename] = []
                    self.error_files[filename].append(line_number)

    def get_context(self, filelist):
        context = ""
        for f in filelist.keys():
            for l in filelist[f]:
                context += SymbolExt.get_related_ast(f, l)
                context += "\n"
        return context


    def generate_edits(self, error_message):
        context_ast = self.get_context(self.error_files)

        SYSTEM_PROMPT = "You are a debug expert, and your job is to extract the functions and files mentioned in the error message, and return in the given format."
        prompt = f"""
        the error message is: 
        {error_message}

        Context AST:
        {context_ast}

        Please generate the edit for this error message, return in this format:
        if you want to edit: 
            [Edit] filename - #line number
            ```Code```
        if you want to insert:
            [Insert] filename - #line number
            ```Code```
        if you want to delete: 
            [Delete] filename - #line number
        """

        response = client.chat.completions.create(
            model="nova-pro-v1",
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
            max_tokens=2000,
            stream=False
        )

        return response.choices[0].message.content

    def get_ast(self, file_path, line_number, code=None):
        return get_related_ast(file_path, line_number, code=code)

    def edit(self, file_path, content, line_n):
        pass

    def delete(self, file_path, line_n):
        pass

    def insert(self, file_path, content, line_n):
        pass
