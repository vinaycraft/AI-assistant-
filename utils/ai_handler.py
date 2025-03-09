import openai
from datetime import datetime

class AIHandler:
    def __init__(self, api_key, api_base="https://api.deepseek.com/v1"):
        self.api_key = api_key
        openai.api_key = api_key
        openai.api_base = api_base

    def chat(self, prompt):
        """Have a conversation with Deepseek AI"""
        try:
            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

    def generate_code(self, prompt):
        """Generate code using Deepseek AI"""
        try:
            response = openai.ChatCompletion.create(
                model="deepseek-coder",
                messages=[{"role": "user", "content": f"Generate code for: {prompt}"}],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I couldn't generate the code: {str(e)}"

    def summarize_text(self, text):
        """Summarize text using Deepseek AI"""
        try:
            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": f"Please summarize this text: {text}"}],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I couldn't summarize the text: {str(e)}"

    def analyze_system_health(self, system_report):
        """Get AI recommendations for system health"""
        try:
            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[{
                    "role": "user",
                    "content": f"Analyze this system health report and provide specific recommendations for optimization and maintenance. If any metrics are concerning, highlight them: {system_report}"
                }],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I couldn't analyze the system health: {str(e)}"

    def analyze_startup_impact(self, startup_info):
        """Analyze startup programs and their impact"""
        try:
            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[{
                    "role": "user",
                    "content": f"Analyze these startup programs and suggest which ones might be unnecessary or impacting system performance: {startup_info}"
                }],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I couldn't analyze the startup programs: {str(e)}"
