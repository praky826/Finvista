import sys
with open("uvicorn_log_utf8.txt", 'rb') as f:
    lines = f.readlines()
    for line in lines[-200:]:
        print(line.decode('utf-8', errors='replace').strip())
