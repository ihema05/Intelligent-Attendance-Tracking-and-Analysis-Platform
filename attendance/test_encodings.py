import pickle

with open("encodings.pkl", "rb") as f:
    data = pickle.load(f)

print("Keys:", data.keys())
print("Number of encodings:", len(data["encodings"]))
print("Example ID:", data["ids"][0])
