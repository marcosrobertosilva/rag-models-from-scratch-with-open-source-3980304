from ollama import embed, chat

embeddings = embed(model="marcos_model", input=["Here is an example sentence I will be embedding!", "Here's a second one!"])

print(len(embeddings['embeddings']))

response = chat(model='marcos_model', messages=[
  {
    'role': 'user',
    'content': 'Why did the chicken cross the road?',
  },
])

print(response.message.content)
