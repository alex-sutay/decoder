"""
author: Alex Sutay
file: decode.py
This file should hopefully try to brute force a solution to a coded message
"""
from spellchecker import SpellChecker  # used to check the solution
from json import dump  # used for saving solutions

NAMES = ['alex', 'alexander', 'sutay', 'aaron', 'austin', 'kenny', 'huffer']
THRESHOLD = 1e-06  # This value is how common the word has to be in order to be considered

spell = SpellChecker()
for j in range(98, 123):
    if j != 105:
        spell.word_frequency.remove(chr(j))
spell.word_frequency.load_words(NAMES)


def main():
    """
    The primary function called. This should ask for an input text file,
    then begin brute forcing a solution beginning with the words that are shortest
    :return: None
    """
    filename = input('cipher text file: ')
    words = load_ciphertext(filename)
    solutions = solve(words)
    with open(input('Save solutions to: '), 'w') as f:
        dump(solutions, f)
    solutions = sorted(solutions, key=lambda x: score(decode_file(filename, x)))
    for sol in solutions:
        print(decode_file(filename, sol))


def solve(words, solution=None, final=None):
    """
    This function should recursively try to find the solution to the cipher,
    prioritizing the more likely solutions to shorter words first
    :param words: list of encoded "words" in the cipher
    :param solution: dictionary of conversions so far
    :param final: a set of solution dictionaries to return
    :return: solution dictionary
    """
    solution = dict() if solution is None else solution
    final = [] if final is None else final

    next_word, idxs = find_easiest(words, solution)
    if next_word == '' and valid(words, solution):
        final.append(solution)
        print(decode(words, solution))
        return final

    all_poss = find_all_poss(next_word, solution, idxs)
    if all_poss == {}:
        return final
    all_poss = sorted(all_poss.keys(), key=lambda x: all_poss[x], reverse=True)
    for poss in all_poss:
        new_sol = add_to_solution(next_word, poss, {k: solution[k] for k in solution})
        final = solve(words, new_sol, final)
    return final


def find_easiest(words, solution):
    """
    Finds the easiest word to solve for next
    :param words: the encoded "words" in the cipher
    :param solution: dictionary of conversions so far
    :return: tuple of (easiest_word, [idxs, of, unknowns])
    """
    easiest = ''
    fin_idxs = []
    current_min = 999
    for word in words:
        idxs = idx_unknown(word, solution)
        this_count = len(idxs)
        if this_count == 1:
            return word, idxs
        elif this_count < current_min and this_count != 0:
            easiest = word
            fin_idxs = idxs
            current_min = this_count

    return easiest, fin_idxs


def idx_unknown(word, solution):
    """
    Find the indexes of letters that haven't been solved for yet
    :param word: the encoded word being checked
    :param solution: dictionary of conversions so far
    :return: list of [idxs, of, unknowns]
    """
    word = word.split('-')
    idxs = []
    for i in range(0, len(word)):
        if word[i] not in solution:
            idxs.append(i)
    return idxs


def find_all_poss(word, solution, idxs, so_far=None):
    """
    Recursive function that finds all possible decoded words and their probabilities
    :param word: the encoded word
    :param solution: dictionary of conversions so far
    :param idxs: indexes of unknown letters
    :param so_far: the words so far; used if it goes recursive
    :return: dict of {decoded:prob}
    """
    if so_far is None:
        iter_word = word.split('-')
        new_word = ''
        for i in range(0, len(iter_word)):
            if iter_word[i] in solution:
                new_word += solution[iter_word[i]]
            else:
                new_word += '_'
        so_far = [new_word]  # if this still 1 layer deep, set the words to iterate through to just the word
    if not idxs:
        # base case
        return {k: spell.word_probability(k) for k in so_far if spell.word_probability(k) > THRESHOLD}
    else:
        idx = idxs.pop(0)
        new_so_far = []
        for this_word in so_far:
            for char in range(97, 123):
                new_word = this_word
                new_word = new_word[:idx] + chr(char) + new_word[idx+1:]
                new_so_far.append(new_word)
        return find_all_poss(word, solution, idxs, new_so_far)


def add_to_solution(word, decoded, solution):
    """
    Adds to the solution the conversions necessary to make word into decoded
    :param word: the encoded word
    :param decoded: the decoded word
    :param solution: dictionary of conversions so far
    :return: new solution
    """
    word = word.split('-')
    for i in range(0, len(word)):
        solution[word[i]] = decoded[i]
    return solution


def valid(words, sol):
    """
    vaildate a solution
    :param words: the encoded words
    :param sol: solution dictionary
    :return: boolean
    """
    if not sol:
        return False
    decoded = decode(words, sol)
    for word in decoded.split(' '):
        if spell.word_probability(word) == 0:
            return False
    return True


def load_ciphertext(filename):
    """
    load the words from a file
    :param filename: name of cipher text file
    :return: list of [encoded, words]
    """
    words = set()
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            words.add(line.strip())
    return list(words)


def decode(words, solution):
    """
    Decode the cipher text once you have a solution
    :param words: the encoded words
    :param solution: dictionary of conversions
    :return: string of final solution
    """
    final_str = ''
    for word in words:
        for char in word.split('-'):
            final_str += solution[char] if char in solution else '_'
        final_str += ' '
    final_str = final_str[:-1]

    with open('tested.txt', 'a') as f:
        f.write(final_str + '\n')

    return final_str


def decode_file(filename, solution):
    """
    This is a helper file to pass the contents of a file to the decode function
    :param filename: name of the file to open
    :param solution: dictionary containing the solution
    :return: str decoded text
    """
    with open(filename) as f:
        lines = [k.strip() for k in f.readlines()]
    return decode(lines, solution)


def score(string):
    """
    This function is used to find the best solution, it rates a string by multiplying all of the probabilities together
    :param string: the string of words being rated
    :return: decimal score
    """
    fin_score = 1
    for word in string.split(' '):
        fin_score *= (spell.word_probability(word) * 1/THRESHOLD)
        # the last part is just a constant to keep the scores from being too small
    return fin_score


if __name__ == '__main__':
    main()
