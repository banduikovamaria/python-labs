def word_frequency(text):
    words = text.lower().split()
    freq = {}

    for w in words:
        freq[w] = freq.get(w, 0) + 1

    filtered = {word: count for word, count in freq.items() if count > 3}

    return filtered


text = "apple banana apple kiwi apple banana apple pear banana banana kiwi apple"
result = word_frequency(text)
print("Слова, що зустрічаються більше 3 разів:", result)
