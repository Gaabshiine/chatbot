# chat/views.py
import os
from django.http import JsonResponse
from django.shortcuts import render
from django.templatetags.static import static
from pdfminer.high_level import extract_text
from langchain_community.vectorstores import FAISS
import openai
from .models import Chat
from gaabshiine_chat.constants import API_KEY
from django.contrib.staticfiles import finders
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
import json
from .utils import generate_response




# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load and chunk text data for embeddings
def load_text():
    file_path = finders.find('chat/data.txt')
    if not file_path:
        raise ValueError("data.txt not found in static files")

    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def chunk_text(text, max_tokens=512):
    lines = text.split('\n')
    chunks, current_chunk, current_length = [], [], 0

    for line in lines:
        line_length = len(line.split())
        if current_length + line_length > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk, current_length = [line], line_length
        else:
            current_chunk.append(line)
            current_length += line_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

class OpenAIEmbeddingsWrapper:
    def __init__(self, model_name="text-embedding-ada-002"):
        self.model_name = model_name

    def embed_documents(self, texts):
        response = openai.Embedding.create(input=texts, model=self.model_name)
        return [embedding["embedding"] for embedding in response["data"]]

    def embed_query(self, text):
        response = openai.Embedding.create(input=[text], model=self.model_name)
        return response["data"][0]["embedding"]

    def __call__(self, texts):
        return self.embed_query(texts) if isinstance(texts, str) else self.embed_documents(texts)

def setup_retriever(text):
    text_chunks = chunk_text(text)
    embedding_wrapper = OpenAIEmbeddingsWrapper()
    retriever = FAISS.from_texts(text_chunks, embedding=embedding_wrapper)
    return retriever

def ask_question(retriever, question):
    docs = retriever.similarity_search(question, k=3)
    context = "\n".join([doc.page_content for doc in docs])

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that uses provided context to answer questions."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    )
    return response["choices"][0]["message"]["content"]

def chat_view(request):
    if request.method == "POST":
        question = request.POST.get("question")
        text = load_text()
        retriever = setup_retriever(text)
        answer = ask_question(retriever, question)

        # Save the question and answer to the database
        chat = Chat.objects.create(question=question, answer=answer)

        # Return a JSON response for AJAX
        return JsonResponse({
            "question": question,
            "answer": answer,
            "timestamp": chat.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        })

    # For GET requests, render the template and load existing chats
    chats = Chat.objects.order_by("timestamp")
    return render(request, "chat/chat.html", {"chats": chats})


    
@require_POST
def delete_all_chats(request):
    # Delete all chat records from the database
    Chat.objects.all().delete()
    return JsonResponse({"success": True})




def load_custom_data():
    file_path = finders.find('chat/data.txt')
    if not file_path:
        raise ValueError("data.txt not found in static files")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


@csrf_exempt
@require_POST
def edit_chat(request, chat_id):
    try:
        # Retrieve and update chat object
        chat = get_object_or_404(Chat, id=chat_id)
        data = json.loads(request.body)
        new_question = data.get("question")

        if new_question:
            chat.question = new_question
            custom_data = load_text()  # Load custom context data
            chat.answer = generate_response(new_question, context=custom_data)  # Generate new response
            chat.save()

            # Return updated answer and success status for UI update
            return JsonResponse({"success": True, "answer": chat.answer})
        else:
            return JsonResponse({"success": False, "error": "No question provided."}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)



