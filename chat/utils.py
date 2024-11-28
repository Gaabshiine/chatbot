# chat/utils.py
import openai

def generate_response(question, context=None):
    """
    Generates a response from OpenAI's API based on the provided question and optional context.
    """
    try:
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        if context:
            messages.append({"role": "system", "content": f"Context:\n{context}"})
        messages.append({"role": "user", "content": question})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        answer = response['choices'][0]['message']['content']
        return answer
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm sorry, but I couldn't generate a response at this time."
