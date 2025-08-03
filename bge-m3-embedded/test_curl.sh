curl http://localhost:8000/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "input": ["你好，世界", "天气很好"],
    "model": "bge-m3"
  }'
