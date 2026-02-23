#Abdul Basit 102366
import re
import os

# ===================================================================== #
# STEP 1: READING THE FILE
# ===================================================================== #
# Reading the raw text file from the given path.
# If the file isn't there, it willjust return a dummy string I made for testing.
def read_urdu_text(file_path):
    try:
        if os.path.exists(file_path):

            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise FileNotFoundError
    except Exception as e:
        print(f"File not found. using dummy text instead.")
        
        # dummy text with some weird spacing to test the cleaner
        mock_string = """
            یہ ایک تجرباتی جملہ ہے اور   اس میں بہت سارے   فالتو  اسپیس  ہیں  ۔ 
            کیا یہ صحیح طرح سے کام کرے گا ؟   ہاں، مجھے           امید ہے کہ  یہ کام کرے گا ۔ 
        """
        return mock_string


# ===================================================================== #
# STEP 2: CLEANING THE STRING (PREPROCESSING)
# ===================================================================== #
# taking care of extra spaces and tabs (Space Insertion/Omission issues)
def preprocess_urdu_text(text):

    # regex \s+ finds all variations of spaces and replaces them with a single space
    cleaned_text = re.sub(r'\s+', ' ', text)
    
    # remove leading/trailing spaces
    cleaned_text = cleaned_text.strip()

    return cleaned_text


# ===================================================================== #
# STEP 3: DEFINING THE "SPLIT" RULES
# rules for deciding where to split

# explicit punctuation marks that mark the end of a sentence
punctuation_marks = ['۔', '؟', '!', '.']

# common urdu words that usually appear at the end of a sentence
end_words = [
    'ہے', 'ہیں', 'تھا', 'تھی', 'تھے', 
    'گا', 'گی', 'گے', 'دیا', 'چکا', 
    'چکی', 'چکے', 'ہوئے', 'ہوا', 'ہوئی',
    'کرتے', 'کرو', 'ہوں', 'کیا',
    'ہو', 'گیا'
]

# words that usually appear at the start of a new sentence 
# i'll use this for the look-ahead check
continuation_words = [
    'اور', 'لیکن', 'وہ', 'یہ', 'اگر', 
    'مگر', 'پھر', 'چنانچہ', 'لہذا', 'اس', 'ان', 'تو', 'کہ',
    'کیا', 'میں', 'تم', 'مجھے', 'کسی', 'کاش'
]


# ===================================================================== #
# STEP 4: THE LOOP (SEGMENTATION)
# ===================================================================== #
# goes through the text word by word and applies the rules
def segment_sentences(cleaned_text):
    # split text by space to get individual words
    words = cleaned_text.split(' ') 

    sentences = []
    current_sentence = []
    
    # iterate using enumerate to keep track of the index
    for i, word in enumerate(words):

        current_sentence.append(word)
        
        # Rule 1: check if word ends with standard punctuation
        ends_with_punctuation = any(word.endswith(punct) for punct in punctuation_marks)
        
        # Rule 2: check if word is an 'end word' AND the next word starts a new sentence
        is_end_word = word in end_words
        
        # get the next word (if we're not at the very end of the text)
        next_word = words[i + 1] if i + 1 < len(words) else None
        
        # make sure sentence has at least 2 words to avoid splitting on a single word by accident
        suggests_boundary = is_end_word and (next_word in continuation_words or next_word is None) and len(current_sentence) >= 2
        
        # if any of the rules hit, save the sentence
        if ends_with_punctuation or suggests_boundary:
            # put the words back together into a string
            full_sentence = ' '.join(current_sentence).strip()
            
            # append and reset for the next loop
            if full_sentence: 
                sentences.append(full_sentence)
                
            current_sentence = []
            
    # if there are any words left over at the end of the loop, group them up
    if current_sentence:
        full_sentence = ' '.join(current_sentence).strip()

        if full_sentence:
            sentences.append(full_sentence)
            
    return sentences


# ===================================================================== #
# STEP 5:  EVALUATION
# ===================================================================== #
# function to calculate accuracy, precision, etc.:
def eval_function(gold_standard, predicted_sentences):

    # copying lists so i can remove matched items without messing up the original loop
    gold_pool = list(gold_standard)
    
    tp = 0 # correct predictions
    for pred in predicted_sentences:
        if pred in gold_pool:

            tp += 1
            gold_pool.remove(pred) # removed so it doesn't double count
            
    # fp = predicted lines that are wrong
    fp = len(predicted_sentences) - tp 
    
    # fn = lines from gold standard i missed
    fn = len(gold_standard) - tp 
    
    # calculating the metrics
    total_unique_sentences = tp + fp + fn
    accuracy = tp / total_unique_sentences if total_unique_sentences > 0 else 0.0

    precision = tp / len(predicted_sentences) if len(predicted_sentences) > 0 else 0.0
    
    recall = tp / len(gold_standard) if len(gold_standard) > 0 else 0.0
    
    # f1 check (prevent division by 0)
    if (precision + recall) > 0:

        f1_score = 2 * (precision * recall) / (precision + recall)
    else:

        f1_score = 0.0
        
    print("\n==================================")
    print("      EVALUATION METRICS          ")
    print("==================================")
    print(f"Gold Standard Total : {len(gold_standard)}")
    print(f"Predictions Total   : {len(predicted_sentences)}")
    print(f"True Positives (TP) : {tp}")
    print(f"False Positives (FP): {fp}")
    print(f"False Negatives (FN): {fn}")
    print("----------------------------------")
    print(f"Accuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1-Score  : {f1_score:.4f}")
    print("==================================\n")


# ===================================================================== #
# MAIN EXECUTION 
# ===================================================================== #
if __name__ == "__main__":
    print("\n--- Running Segmentation ---\n")
    
    # 1. Read the file
    file_name = "urdu-corpus portion.txt"
    raw_text = read_urdu_text(file_name)
    
    print("[1] Raw text:")
    # using repr to show the hidden \\n chars in print
    print(repr(raw_text[:120] + "...")) 
    
    # 2. Clean it up
    cleaned_text = preprocess_urdu_text(raw_text)
    
    print("\n[2] Clean text:")
    print(repr(cleaned_text[:120] + "..."))
    
    # 4. Run the segmenter
    predicted_sentences = segment_sentences(cleaned_text)
    
    print("\n[4] Output Sentences:")
    for idx, sentence in enumerate(predicted_sentences, 1):
        print(f" {idx}. {sentence}")
        
    # 5. Evaluate
    # reading the original file lines to use as the true reference for grading
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            # running the regex here too so spaces match exactly with our predictions
            gold_standard = [re.sub(r'\s+', ' ', line).strip() for line in f if line.strip()]
    else:
        # fallback lines for testing with the dummy string
        gold_standard = [
            "یہ ایک تجرباتی جملہ ہے",
            "اور اس میں بہت سارے فالتو اسپیس ہیں ۔",
            "کیا یہ صحیح طرح سے کام کرے گا ؟",
            "ہاں، مجھے امید ہے کہ یہ کام کرے گا ۔"
        ]
    
    # Run the grader
    eval_function(gold_standard=gold_standard, predicted_sentences=predicted_sentences)
