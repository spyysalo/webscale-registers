import sys
import time
import json

from argparse import ArgumentParser
from functools import wraps

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from datasets import load_dataset
from transformers import pipeline


def argparser():
    ap = ArgumentParser()
    ap.add_argument('model')
    ap.add_argument('data')
    ap.add_argument('--batch_size', type=int, default=128)
    return ap


def timed(func, out=sys.stderr):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        retval = func(*args, **kwargs)
        end = time.time()
        print(f'timed {func.__name__}: {end-start:.2f} sec', file=out)
        return retval
    return wrapper


@timed
def load_tokenizer(args):
    return AutoTokenizer.from_pretrained(args.model)


@timed
def load_model(args):
    return AutoModelForSequenceClassification.from_pretrained(
        args.model,
        problem_type="multi_label_classification",
        device_map='auto',
        torch_dtype='auto',
    )


@timed
def load_data(args):
    return load_dataset(
        'json',
        data_files=args.data,
        streaming=True,
        split='train',
    )


@timed
def make_pipeline(model, tokenizer):
    return pipeline(
        'text-classification',
        model=model,
        tokenizer=tokenizer,
        truncation=True,
        max_length=tokenizer.model_max_length,
        top_k=None, # return_all_scores=True,
    )


@timed
def predict(pipe, dataset, args):
    ids = []    # pass ID around pipeline
    def iter_text(data):
        for d in data:
            ids.append(d['id'])
            yield d['text']

    def format_output(id_, label_scores):
        return {
            'id': id_,
            'register_probabilities': {
                i['label']: round(i['score'], 4) for i in label_scores
            },
        }

    output =  pipe(
        iter_text(dataset),
        batch_size=args.batch_size,
    )
    for i, o in enumerate(output, start=1):
        if i % 10000 == 0:
            print(f'predicted {i} ...', file=sys.stderr)
        print(json.dumps(format_output(ids.pop(0), o)))
    print(f'done, predicted {i}.', file=sys.stderr)


def main(argv):
    args = argparser().parse_args(argv[1:])

    tokenizer = load_tokenizer(args)
    model = load_model(args)
    dataset = load_data(args)
    pipe = make_pipeline(model, tokenizer)
    predict(pipe, dataset, args)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
