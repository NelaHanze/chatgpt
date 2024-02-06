import openai

openai.api_key = "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"

response = openai.Completion.create(
  engine="text-davinci-003",
  prompt="Ako sa máš?",
  max_tokens=5
)

print(response)