import wikipedia

def search_medical_wikipedia():
    print("Welcome to the Medical Wikipedia Chat Interface! Type 'exit' to quit.\n")
    
    while True:
        # Get user input
        query = input("Ask a medical question: ")
        
        if query.lower() == 'exit':
            print("Goodbye!")
            break

        try:
            # Search Wikipedia for the query
            search_results = wikipedia.search(query)

            if not search_results:
                print("No results found, try a different medical question.\n")
                continue

            # Get the summary of the first result
            summary = wikipedia.summary(search_results[0], sentences=3)
            print("\nSummary of the result:")
            print(summary + "\n")

        except wikipedia.exceptions.DisambiguationError as e:
            print(f"Disambiguation Error: Your search is ambiguous, here are some options: {e.options}\n")
        except wikipedia.exceptions.PageError:
            print("Page not found, please try again.\n")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    search_medical_wikipedia()
