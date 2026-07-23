from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class ChatGPTClient_nano:
    def __init__(self, model="gpt-5.4-nano"):
        self.client = OpenAI()
        self.model = model

    def ask(self, prompt: str, user_text: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            instructions=prompt,
            input=user_text
        )

        return response.output_text
    


class ChatGPTClient_luna:
    def __init__(self, model="gpt-5.6-luna"):
        self.client = OpenAI()
        self.model = model

    def ask(self, prompt: str, user_text: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            instructions=prompt,
            input=user_text
        )

        return response.output_text


# class ChatGPTClient_message:
#     def __init__(self, model="gpt-5.5"):
#         self.client = OpenAI()
#         self.model = model

#     def ask(self, prompt: str, user_text: str) -> str:
#         response = self.client.responses.create(
#             model=self.model,
#             instructions=prompt,
#             input=user_text
#         )

#         return response.output_text