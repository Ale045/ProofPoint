from flask import Flask, request, render_template
from utils import extract_keywords_for_search, find_similar_sentences_cloud, SemanticScholarError, encode_abstracts
from search import search_papers_by_topic
# import threading

app = Flask(__name__)

# Load the Sentence-Transformer model globally
# model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
# model_lock = threading.Lock()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        sentence = request.form['sentence']
        
        # Check if the user has modified the topics
        if 'modified_topics' in request.form:
            keywords = request.form['modified_topics'].split()
        else:
            keywords = extract_keywords_for_search(sentence)

        topic = " ".join(keywords)

        # Paper Search
        try:
            papers = search_papers_by_topic(topic, limit=100)
        except SemanticScholarError as e:
            error_message = str(e)
            return render_template('index.html', error=error_message)

        # Similarity Search
        # with model_lock:
        # example_embedding = model.encode(sentence, convert_to_tensor=True)
        # replace . with space
        sentence = sentence.replace(".", " ")
        example_embedding = encode_abstracts(sentence)[0]
        similar_sentences, scores = find_similar_sentences_cloud(example_embedding, papers)

        if similar_sentences:
            print(similar_sentences)
            paper_data = []
            for i in range(len(papers)):
                paper_data.append({
                    "paper": papers[i],
                    "similar_sentence": similar_sentences[i],
                    "score": scores[i]
                })

            paper_data.sort(key=lambda x: x["score"], reverse=True)
            paper_index = 0
            most_similar_sentence = paper_data[0]["similar_sentence"]

            return render_template('index.html', keywords=keywords, sentence=sentence, paper_data=paper_data, most_similar_sentence=most_similar_sentence, paper_index=paper_index)
        else:
            return render_template('index.html', keywords=keywords, sentence=sentence, paper_data=[], most_similar_sentence="", paper_index=None)

    return render_template('index.html', keywords=[], sentence="", paper_data=[], most_similar_sentence="", paper_index=None)

if __name__ == '__main__':
    app.run(debug=True)