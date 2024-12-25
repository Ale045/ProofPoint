import requests

# def search_papers_by_topic(topic, limit=10):
#     """
#     Searches for papers related to a topic using the Semantic Scholar API (unauthenticated).

#     Parameters:
#     - topic: The search topic (e.g., "machine learning").
#     - limit: Number of papers to retrieve (default is 10).

#     Returns:
#     - A list of dictionaries containing the title, abstract, and URL of each paper.
#     """
#     url = "https://api.semanticscholar.org/graph/v1/paper/search"
#     params = {
#         "query": topic,
#         "fields": "title,abstract,url",
#         "limit": limit
#     }

#     response = requests.get(url, params=params)

#     if response.status_code == 200:
#         data = response.json()
#         results = []
#         for paper in data.get("data", []):
#             results.append({
#                 "title": paper.get("title", "No Title"),
#                 "abstract": paper.get("abstract", "No Abstract Available"),
#                 "url": paper.get("url", "No URL Available")
#             })
#         return results
#     else:
#         print(f"Error: {response.status_code}, {response.text}")
#         return []


def search_papers_by_topic(topic, limit=100):
    """
    Searches for papers related to a topic using the OpenAlex API.

    Parameters:
    - topic: The search topic (e.g., "machine learning").
    - limit: Number of papers to retrieve (default is 10).

    Returns:
    - A list of dictionaries containing the title, abstract, and URL of each paper.
    """
    base_url = "https://api.openalex.org/works"
    params = {
        "search": topic,
        # "filter": f"abstract.search:{topic}",  # Search in abstract using filter
        "select": "title,open_access,abstract_inverted_index",  # Select inverted index
        "per_page": limit,
        "sort": "cited_by_count:desc"
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        results = []
        for work in data.get("results", []):
            abstract = get_abstract_from_inverted_index(work.get("abstract_inverted_index"))
            results.append({
                "title": work.get("title", "No Title"),
                "abstract": abstract,
                "url": work.get("open_access", {}).get("oa_url", "No URL Available"),
            })
        return results
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []

def get_abstract_from_inverted_index(inverted_index):
    """
    Reconstructs the abstract from OpenAlex's inverted index format.
    """
    if not inverted_index:
        return "No Abstract Available"

    # Create a dictionary to store word positions
    word_positions = {}
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions[pos] = word

    # Sort positions and reconstruct the abstract
    sorted_positions = sorted(word_positions.keys())
    abstract_words = [word_positions[pos] for pos in sorted_positions]
    return " ".join(abstract_words)

