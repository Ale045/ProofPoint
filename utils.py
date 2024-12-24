from keybert import KeyBERT
from sentence_transformers import util

def extract_keywords_for_search(sentence, top_n=5, use_mmr=True, diversity=0.7):
    model = KeyBERT('all-MiniLM-L6-v2')
    keywords = model.extract_keywords(sentence, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=top_n, use_mmr=use_mmr, diversity=diversity)
    keywords = [kw[0] for kw in keywords]
    return remove_substrings(keywords)

def remove_substrings(keywords):
    filtered_keywords = []
    for kw1 in keywords:
        is_substring = False
        for kw2 in keywords:
            if kw1 != kw2 and kw1 in kw2:
                is_substring = True
                break
        if not is_substring:
            filtered_keywords.append(kw1)
    return filtered_keywords

def encode_abstracts(abstract, model):
    embedding_list = []
    try:
        sentences = abstract.split(". ")
        sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
        embedding_list.append(sentence_embeddings)
        return embedding_list
    except Exception:
        return []

# def find_similar_sentence_in_papers(example_embedding, papers, model):
#     similar_sentences = []
#     scores = []
#     for i, paper in enumerate(papers):
#         abstract_embeddings = encode_abstracts(paper["abstract"], model)
#         if not abstract_embeddings:
#             continue

#         cos_scores = util.pytorch_cos_sim(example_embedding, abstract_embeddings[0])
#         top_sentence_idx = cos_scores.argmax()
#         similar_sentence = paper["abstract"].split(". ")[top_sentence_idx]
#         similar_sentences.append(similar_sentence)
#         scores.append(cos_scores.max().item())

#     return similar_sentences, scores

def find_similar_sentence_in_papers(example_embedding, papers, model, threshold=0):
    similar_sentences = []
    scores = []
    for i, paper in enumerate(papers):
        abstract_embeddings = encode_abstracts(paper["abstract"], model)
        if not abstract_embeddings:
            # Case 1: Empty abstract or processing error
            similar_sentences.append("No similar sentence found.")  # Add a default value
            scores.append(0)  # Add a default score
            continue

        cos_scores = util.pytorch_cos_sim(example_embedding, abstract_embeddings[0])

        # found_similar = True  # Flag to track if a similar sentence is found for the current paper
        # for j, score in enumerate(cos_scores[0]):
        #     # if score >= threshold:
        #         # Case 2: Similar sentence found (above threshold)
        similar_index = cos_scores.argmax()
        similar_sentence = paper["abstract"].split(". ")[similar_index]
        similar_sentences.append(similar_sentence)
        scores.append(cos_scores.max().item())
        # found_similar = True

        # if not found_similar:
        #     # Case 3: No similar sentence found (above threshold) for this paper
        #     similar_sentences.append("No similar sentence found.")  # Add a default value
        #     scores.append(0)  # Add a default score

    return similar_sentences, scores

class SemanticScholarError(Exception):  # Define the exception here
    pass