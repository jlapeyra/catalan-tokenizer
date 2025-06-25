from io import TextIOWrapper
import sys
from model import PosModel
import argparse


def tokenize_line(model:PosModel, line:str, out:TextIOWrapper):
    tokens = model.tokenize(line)
    pos_vecs = model.predictPos(tokens)
    for (t, options), p in zip(tokens, pos_vecs):
        #options = set(wi.pos[:2] for wi in options)
        #print(p, t, '\t', ','.join(options) if len(set(options)) > 1 else '', file=out)
        print(p, t, file=out)
    print(file=out)
    out.flush()

if __name__ == '__main__':
    #USAGE: python main.py [--input <input_file>] [--output <output_file>] [--text <text>] [--model <model_name>]

    parser = argparse.ArgumentParser(description="Catalan Tokenizer POS Tagger")
    parser.add_argument('--input', '-i', type=str, help='Input file path (default: stdin)')
    parser.add_argument('--output', '-o', type=str, help='Output file path (default: stdout)')
    parser.add_argument('--text', '-t', type=str, help='Input text (optional, overrides input file)')
    parser.add_argument('--model', '-m', type=str, default='ancora', help='Model name (default: ancora)')
    parser.epilog = "The foillowing files should already exist: model/<model_name>.2pos.2gram.txt and <model_name>.2pos.count.txt\n" \
                    "You can train the model using the train.py script with the ancora-train.pos.txt file."

    args = parser.parse_args()

    input = open(args.input, 'r', encoding='utf-8') if args.input else sys.stdin
    output = open(args.output, 'w', encoding='utf-8') if args.output else sys.stdout

    model = PosModel(args.model, pos_len=2)
    if args.text:
        input = [args.text]
    for line in input:
        tokenize_line(model, line.strip(), output)
    
