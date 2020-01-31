from utilities import *

def parse_story(file_name):
    '''
    (str)->list
    Returns an orderedlist  of words  with  bad  characters processed
    (removed) from the textin the file given by file_name. 
    '''
    fname = file_name
    test_case = open(fname, 'r')
    text = ''
    for item in test_case:
        text = text + str(item)
    word  = ""
    for char in text:
        if char in VALID_PUNCTUATION or char in BAD_CHARS:
            word = word + " " + char + " "
        else:
            word = word + char
    for r in BAD_CHARS:
        for char in word:
            if char == r:
                word = word.replace(char, " ")
    delete_slash = word.find("\n")
    word = word.replace(word[delete_slash], " ")
    word = word.lower()
    return word.split()

def get_prob_from_count(counts):
    '''
    (list)->list
    Returns a derived probablities from counts. Counts is a list of counts  of occurrences of
    a token after the  previous n-gram.
    >>> get_prob_from_count([10, 20, 40, 30])
    [0.1, 0.2, 0.4, 0.3]
    '''
    s = sum(counts)
    for i in range (0, len(counts)):
        counts[i] = counts[i]/s
    return counts


def build_ngram_counts(words, n):
    '''
    (list, int)->dictionary
    Return a dictionary of N-grams and the counts  of the  words  that follow
    the N-gram.
    '''
    words_to_context = {}
    for i in range(len(words) - n):
        context = tuple(words[i: i + n])
        if context not in words_to_context:
            words_to_context[context] = [[], []]
        if words[i + n] not in words_to_context[context][0]:
            words_to_context[context][0].append(words[i + n])
            words_to_context[context][1].append(0)
        if words[i + n] in words_to_context[context][0]:
            num = words_to_context[context][0].index(words[i + n])
            words_to_context[context][1][num] = words_to_context[context][1][num] + 1
    return words_to_context


def prune_ngram_counts(counts, prune_len):
    '''
    (dictionary, int)->dictionary
    Return a dictionary of N-grams and counts
    of words with lower frequency (i.e. occurring less often) words  removed. 
    '''
    for context in list(counts.keys()):
        temp = counts[context][1][:]
        big_ind = []
        prune_list = []
        if len(temp) > prune_len:
            pr = prune_len
            while pr > 0:
                big_value = max(temp)
                for index in range(0, len(temp)):
                    if temp[index] == big_value:
                        prune_list.append(big_value)
                        big_ind.append(index)
                        temp[index]  = 0
                        pr = pr - 1
            dummy_list = []
            for i in range (0, len(big_ind)):
                dummy_list.append(counts[context][0][big_ind[i]])
            counts[context][0] = dummy_list
            counts[context][1] = prune_list
    return counts
                
                
def probify_ngram_counts(counts):
    '''
    (dictionary)->dictionary
    Takes a  dictionary  of N-grams  and  counts  and  convert the  counts  to  probabilities.
    The probability of  each word is defined  as the observed  count divided  by  the  total countof all words.
    '''
    for context in list(counts.keys()):
        counts[context][1] = get_prob_from_count(counts[context][1])
    return counts


def build_ngram_model(words, n):
    '''
    (list, n)-> dictionary
    Create  and  return  a  dictionary  of  the  format  given  above  in probify_ngram_counts.  
    This dictionary is your  final model that will be used  to auto-generate text.
    '''
    counts = probify_ngram_counts(build_ngram_counts(words, n))
    for context in list(counts.keys()):
        initial_words = counts[context][0][:]
        empty = []
        for i in range (0, len(counts[context][1])):
            empty.append([counts[context][1][i], i])        
        empty.sort(reverse = True)
        for i in range (0, len(counts[context][1])):
            counts[context][1][i] = empty[i][0]
            counts[context][0][i] = initial_words[empty[i][1]]
    prune_ngram_counts(counts, 15)
    return counts
        
def gen_bot_list(ngram_model, seed, num_tokens=0):
    '''
    (dictionary, tuple, int)-> list
    Returns a randomly generated list of  tokens  (strings)
    that starts  with the  N tokens  in seed,
    selecting  all subsequent  tokens  using gen_next_token.
    '''
    bot_list = list(seed)[:num_tokens]
    if seed in ngram_model:
        if check_open_ngram(seed, ngram_model):       
            for i in range (0, min(num_tokens, (len(ngram_model)) - list(ngram_model.keys()).index(seed))):
                new_seed = gen_next_token(seed, ngram_model)
                bot_list.append(new_seed)
                seed = tuple(bot_list[len(bot_list) - len(seed):])
    return bot_list[:num_tokens + 1]

def gen_bot_text(token_list, bad_author):
    '''
    (list, bool)->str
    If bad_authoris True,  returns  the   string  containing  all  tokens   in token_list, separated  by a space.
    Otherwise, returns  this  string  of  text,  respecting  the  following grammar rules:
    -)There are no spaces before tokens  found  in VALID_PUNCTUATION
    -)Starts new sentences with a capital letter.
    -)Words in ALWAYS_CAPITALIZE star from a capital.
    '''
    always_capitalize = []
    for i in range (len(ALWAYS_CAPITALIZE)):
        always_capitalize[i] = ALWAYS_CAPITALIZE[i].lower()
    text = ''
    if bad_author:
        for i in token_list:
            text = text + ' ' + i
    else:
        token_list.append('')
        for i in range (0, len(token_list) - 1):
            if token_list[i] in VALID_PUNCTUATION:
                if token_list[i] in END_OF_SENTENCE_PUNCTUATION:
                    token_list[i + 1].upper()
                text = text + token_list[i] + " "
            if token_list[i] in always_capitalize:
                token_list[i][0].upper()
                text = text + token_list[i] + " "
            else:
                text = text + " " + token_list[i] + " "
    return text[:len(text) - 1]
                
                

def write_story(file_name, text, title, student_name, author, year):
    '''
    (str, str, str, str, str, str)->str
    Writes text to the file with name file_name. 
    '''
    MAX_LINE_LENGTH = 90
    MAX_PAGE_LENGTH = 30
    MAX_CHAPTER_LENGTH = 12
    name = open(file_name, 'w')
    for i in range (0, 10):
        name.write('\n')
    line_1 = "{0}:{1}, UNLEASHED".format(title, year)
    name.write(line_1)
    name.write('\n')
    line_2 = "{0}, inspired by {1}".format(student_name, author)
    name.write(line_2)
    name.write('\n')
    line_3 = "Copyright year published {0}".format(year)
    name.write(line_3)
    name.write('\n')
    for i in range (0, 17):
        name.write('\n')
    NUMBER_OF_LINES = len(text)//MAX_LINE_LENGTH
    if len(text) % MAX_LINE_LENGTH != 0:
        NUMBER_OF_LINES +=1
  
    NUMBER_OF_PAGES = NUMBER_OF_LINES//MAX_PAGE_LENGTH
    if NUMBER_OF_LINES % MAX_PAGE_LENGTH != 0:
        NUMBER_OF_PAGES +=1  
        
    NUMBER_OF_CHAPTERS = NUMBER_OF_PAGES//MAX_CHAPTER_LENGTH
    if NUMBER_OF_PAGES % MAX_CHAPTER_LENGTH != 0:
        NUMBER_OF_CHAPTERS +=1 
    print(8)
    for number_of_chapters in range (1,NUMBER_OF_CHAPTERS +1):
        name.write("CHAPTER {0}\n\n".format(number_of_chapters))
        print(7)
        while MAX_CHAPTER_LENGTH > 0:
            print(6)
            for number_of_pages in range (MAX_PAGE_LENGTH):
                print(5)
                MAX_PAGE_LENGTH = 30
                while MAX_PAGE_LENGTH > 0:
                    print(4)
                    for number_of_lines in range (NUMBER_OF_LINES):
                        print(3)
                        MAX_LINE_LENGTH = 90
                        while MAX_LINE_LENGTH > 0:
                            print(2)
                            for char in text:
                                print(1)
                                print (0)
                                name.write(char)
                                MAX_LINE_LENGTH -= 1
                        name.write('\n')
                        MAX_PAGE_LENGTH -= 1
                MAX_CHAPTER_LENGTH -= 1
    name.close()
