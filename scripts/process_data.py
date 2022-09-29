import spacy
import sys
import argparse

# Parse arguments
# one string argument with the input file name
def get_args():
    parser = argparse.ArgumentParser(description="Process data")
    parser.add_argument(
        "-i", "--input_file", type=str, required=True, help="input file name"
    )
    return parser.parse_args()


# Read in txt file with spacy, segment into sentences
# and create new file with the sentences each by line
def process_data(nlp: spacy.lang.en.English, input_file: str, output_file: str) -> None:
    texts = []

    with open(input_file, "r", errors="ignore") as f:
        text = ""
        for line in f:
            if line.strip("\n").isupper() or line.strip() == "\n":
                text = text.replace("\n", " ")
                texts.append(text.strip())
                text = ""
            else:
                text += line

    with open(output_file, "w+") as f:
        for text in texts:
            doc = nlp(text)
            for sent in doc.sents:
                f.write(sent.text + "\n")

    return


if __name__ == "__main__":
    nlp = spacy.load("en_core_web_lg")

    # get args from command line
    args = get_args()
    input_file = args.input_file
    output_file = input_file.split(".txt")[0] + "_line" + ".txt"

    process_data(nlp, input_file, output_file)
    print("Processed data saved to {}".format(output_file))
