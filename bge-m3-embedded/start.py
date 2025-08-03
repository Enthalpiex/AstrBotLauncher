from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-m3", trust_remote_code=True)
model = AutoModel.from_pretrained("BAAI/bge-m3", trust_remote_code=True)
