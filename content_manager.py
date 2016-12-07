import pymorphy2
from collections import defaultdict
import operator
import os

MORPH = pymorphy2.MorphAnalyzer()

class ContentManager:
    def __init__(self):
        self.data = dict()
        self.data_path = "data"
        self.config_path = os.path.join(self.data_path, "config.yaml")

    def load_data(self):
        self.data['default'] = {}
        self.load_subjects("default")
        with open(os.path.join(self.data_path, "topic_index.txt"), encoding="utf-8") as index:
            for topic in index:
                topic = topic.strip()
                self.load_patterns(topic)
                self.load_subjects(topic)
        return self.data

    def load_patterns(self, topic):
        self.data[topic] = dict()
        with open(os.path.join(self.data_path, "{}.txt".format(topic)), encoding="utf-8") as topic_file:
            buffer = list()
            self.data[topic]['tasks'] = dict()
            for line in topic_file:
                line = line.strip()
                if line != "":
                    buffer.append(line)
                else:
                    self.data[topic]['tasks'][buffer[0]] = buffer[1:]
                    buffer = list()

    def load_subjects(self, topic):
        with open(os.path.join(self.data_path, "{}_subjects.txt".format(topic)), encoding="utf-8") as subject_file:
            self.data[topic]['subjects'] = subject_file.read().strip().split("\n")
        self.data[topic]['subjects'] += self.data['default']['subjects']

    def make_new_files(self, topics):
        file_path = "%s.txt"
        file_subjects_path = "%s_subjects.txt"
        for topic in topics:
            t_path = os.path.join(self.data_path, file_path % topic)
            t_subj_path = os.path.join(self.data_path, file_subjects_path % topic)
            for _path in [t_path, t_subj_path]:
                if not os.path.exists(_path):
                    with open(_path, "w", encoding="utf-8") as f:
                        f.write("test")

class Token:
    def __init__(self, text):
        self.text = text
        self.parsed = MORPH.parse(text)[0]
        self.lemma = self.parsed.normal_form
        self.tags = self.parsed.tag
        #self.grams_str = " ".join(self.grams)

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text

    def is_pos(self, pos):
        if pos in self.tags:
            return True
        return False

class ContentHelper:
    def __init__(self, corpus_buffer=False, tokens_limit=None):
        self.corpus_path = 'raw_data/buffer.txt' if corpus_buffer else 'raw_data/corpus.txt'

        self.data = self.load_corpus()
        self.tokens_count = 0
        self.tokens_limit = tokens_limit

    def load_corpus(self):
        with open(self.corpus_path, "r", encoding="utf-8") as corpus_file:
            return corpus_file.read()

    def corpus_tokens(self):
        for line in self.data.split("\n"):
            for token in line.split(" "):
                self.tokens_count += 1
                if self.tokens_limit and self.tokens_count > self.tokens_limit:
                    return Token(token)
                yield Token(token)

    def get_n_grams(self, n=2):
        ngram = []
        for token in self.corpus_tokens():
            if len(ngram) >= n:
                yield ngram
                ngram = ngram[1:]
            ngram.append(token)

    def find_all_pos(self, pos={"NOUN", "anim"}):
        freq_dict = defaultdict(int)
        for token in self.corpus_tokens():
            if token.is_pos(pos):
                freq_dict[token.lemma] += 1
        freq_dict_sorted = sorted(freq_dict.items(), key=operator.itemgetter(1), reverse=True)
        return freq_dict_sorted

def save_csv(data, filename):
    content = []
    for entry in data:
        content.append(entry["content"])

    with open("raw_data/output/%s.csv" % filename, "w", encoding="utf-8") as f:
        f.write("\n".join(content))


###experiments###
def save_all_anim_nouns(corpus_buffer=True, tokens_limit = None):
    data = []
    CH = ContentHelper(corpus_buffer, tokens_limit)
    for token in CH.find_all_pos({"NOUN", "anim"}):
        data.append({"content": token[0], "meta": [token[1]]})
    save_csv(data, "anim_nouns")

if __name__ == "__main__":
    CM = ContentManager()
    CM.make_new_files(["home", "clothes", "food", "animals", "transport"])
    #CH = ContentHelper(False, 10000)
    # for ngram in CH.get_n_grams(2):
    #     print(ngram)
    #save_all_anim_nouns(False, 50000)
