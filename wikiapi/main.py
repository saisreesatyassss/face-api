import wikipedia

# Search Wikipedia for a topic
query = "Python programming language"
search_results = wikipedia.search(query)

# Print search results
print("Search Results:")
for i, result in enumerate(search_results):
    print(f"{i+1}: {result}")

# Get the summary of the first result
try:
    summary = wikipedia.summary(search_results[0], sentences=3)
    print("\nSummary of the first result:")
    print(summary)
except wikipedia.exceptions.DisambiguationError as e:
    print(f"Disambiguation Error: {e.options}")
except wikipedia.exceptions.PageError:
    print("Page not found.")
