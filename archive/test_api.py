import urllib.request, json
req = urllib.request.Request('http://127.0.0.1:8000/api/analyze', data=b'{"fen":"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1","multipv":3}', headers={'Content-Type': 'application/json'})
res = urllib.request.urlopen(req).read().decode('utf-8')
data = json.loads(res)
print("KEYS:", list(data.keys()))
print("INTERPRETATION:", data.get("interpretation"))
