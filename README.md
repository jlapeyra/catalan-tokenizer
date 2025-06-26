# Catalan Part-of-Speech Tagger

This repository provides a rule- and probability-based system for part-of-speech (POS) tagging in Catalan. It combines dictionary lookup, heuristic rules for contractions and punctuation, and probabilistic modeling using n-gram distributions.

---

## 📌 Features

- 🧠 **Custom tokenizer** with contraction and punctuation splitting tailored to Catalan.
- 📚 **Dictionary-based tagging** using lexical entries and multiword locutions.
- 📈 **POS disambiguation** using n-gram Markov models and word-based conditional probabilities.
- 🗃️ **Support for training and evaluating models** on corpora like AnCora.
- 🧪 **POS prediction** with forward/backward smoothing and proper noun grouping.

---

## 🔧 Project Structure

- `main.py` – Applies the POS tagger on raw text.
- `model.py` – Contains the core `PosModel` class for tagging logic and probabilistic inference.
- `pos.py` – Manages dictionary and locution loading, tokenization, and morphological analysis.
- `diccionari.py` – Word/POS/lemma structures and loader for `diccionari.txt` and `locucions.txt`.
- `distribution.py` – General-purpose probabilistic structures: n-grams, conditional distributions.
- `probability.py` – Utility functions for probability vector combination and one-hot encoding.
- `train.py` – Code for training n-gram and word-based POS distributions.
- `utils.py` – Helper functions: grouping, windowing, timing, etc.

---

## 🚀 Usage

### Tagging a file

```bash
python main.py
```

By default, this tags the `data/minitrain/wiki.txt` file and outputs to `data/minitrain/wiki.pos.txt`.

---

## 🧪 Example

Input:

```
El Processament de Llenguatge Natural m'interessa molt. 
```

Output:

```
DA El
NC Processament
SP de
NC Llenguatge
AQ Natural
P0 m'
VM interessa
RG molt
Fc .
```

---

## 🧬 Training

To train the POS models from annotated data:

```bash
python train.py
```

This expects files like `data/ancora-train.pos.txt` and saves:

* `model/<name>.count.txt` – word-to-POS conditional counts
* `model/<name>.2gram.txt` – POS bigram counts

---

## 🛠 Requirements

* Python 3.9+
* NumPy
* more\_itertools

Install dependencies:

```bash
pip install numpy more-itertools
```


---

## 🙏 Acknowledgements

- Dictionary: SOFTCATALÀ - https://github.com/Softcatala/catalan-dict-tools.
- Annotated corpus: ANCORA - http://clic.ub.edu/corpus
- Unnanotated corpus: VIQUIPÈDIA - https://ca.wikipedia.org
- Locutions dictionary: VICCIONARI https://ca.wiktionary.org/