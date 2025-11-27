#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
# COPIED FROM https://gist.github.com/joshlk/87c1feecd82e53d0bc860580893aa8f5

def sent_indices_from_list(sents, space_included=False):
    """
    Convert a list of sentences into a list of indiceis indicating the setence spans.
    For example:
    Non-tokenised text: "A. BB. C."
    sents: ["A.", "BB.", "C."] -> [3, 7]
    """
    indices = []
    offset = 0
    for sentence in sents[:-1]:
        offset += len(sentence)
        if not space_included:
            offset += 1
        indices += [offset]
    return indices

def evaluate_indices(true, pred):
    """
    Calculate the Precision, Recall and F1-score. Input is a list of indices of the sentence spans.
    """
    true, pred = set(true), set(pred)
    TP = len(pred.intersection(true))
    FP = len(pred - true)
    FN = len(true - pred)
    return TP, FP, FN

def score(TP, FP, FN):
    if TP+FP==0:
       return 0,0,-1
    if TP+FN==0:
       return 0,0,-1
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    f1 = 2*(precision*recall)/(precision+recall) if precision+recall!=0 else -1
    return precision, recall, f1

def evaluate_recall_plus_minus_1(true, pred):
    """
    Aprox. calculate the Recall given the predicted can be +/-1 from the true value.
    """
    pred_pm_1 = set(e for idx in pred for e in [idx-1, idx, idx+1])
    true, pred = set(true), set(pred)
    TP = len(pred_pm_1.intersection(true))
    FN = len(true - pred_pm_1)
    recall = TP / (TP + FN)
    return recall

def evaluate(pred, true):
    y_true = sent_indices_from_list([x.strip() for x in true])
    y_pred = sent_indices_from_list([x.strip() for x in pred])
    TP, FP, FN = evaluate_indices(y_true, y_pred)
#    print(TP, FP, FN)
    return score(TP, FP, FN)

if __name__=="__main__":
    if len(sys.argv)<2:
       print("Usage: evaluate.py <true_filename> <pred_filename>")
       sys.exit(1)
    true = sys.argv[1]
    pred = sys.argv[2]
    with open(true, encoding='utf-8') as f, open(pred, encoding='utf-8') as g:
       p, r, f1 = evaluate(f.readlines(), g.readlines())
       print("Precision: {}, Recall: {}, F1: {}".format(p, r, f1))