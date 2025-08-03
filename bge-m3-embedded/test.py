import requests

url = "http://localhost:8000/v1/embeddings"
data = {
    "input": ["你好，这是一条测试", "OpenAI 兼容格式测试"],
    "model": "bge-m3"
}

res = requests.post(url, json=data)
print(res.json())
