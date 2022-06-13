def replace(sentence,target_word,replacement_word):
    while(target_word in sentence):
        sentence = sentence.replace(target_word,replacement_word)
    return sentence

print(replace('The quick brown fox jumps over the lazy dog', 'quick', 'slow'))

print(replace('The quick quick quick quick brown fox jumps over the lazy dog', 'quick', 'slow'))