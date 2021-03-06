"""
The class is used to evaluate the application of link prediction
"""

import numpy as np
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from graph_gan_pt import utils


class LinkPredictEval(object):
    def __init__(
        self, embed_filename, test_filename, test_neg_filename, n_node, n_embed
    ):
        self.embed_filename = (
            embed_filename  # each line: node_id, embeddings(dim: n_embed)
        )
        self.test_filename = test_filename  # each line: node_id1, node_id2
        self.test_neg_filename = test_neg_filename  # each line: node_id1, node_id2
        self.n_node = n_node
        self.n_embed = n_embed
        self.embed_filename = embed_filename

    def eval_link_prediction(self, emd=None):
        """for normal lp"""
        if emd is not None:
            self.emd = emd
        else:
            self.emd = utils.read_embeddings(
                self.embed_filename, self.n_node, self.n_embed
            )

        test_edges = self.read_test_edges(read_func=utils.read_edges_from_file)

        score_res = self.create_scores(test_edges)

        true_label, test_label = self.create_labels(score_res)

        accuracy, macro = self.get_acc_and_macro(true_label, test_label)

        return {"acc": accuracy, "macro": macro}

    def eval_rcmd_link_prediction(self, rcmd, emd=None):
        """for recommendation lp"""
        if emd is not None:
            self.emd = emd
        else:
            self.emd = utils.read_embeddings(
                self.embed_filename, self.n_node, self.n_embed
            )

        test_edges = self.read_test_edges(read_func=rcmd.read_edges_from_file)

        score_res = self.create_scores(test_edges)

        true_label, test_label = self.create_labels(score_res)

        accuracy, macro = self.get_acc_and_macro(true_label, test_label)

        return {"acc": accuracy, "macro": macro}

    def create_scores(self, edges):
        # may exists isolated point
        score_res = []
        for i in range(len(edges)):
            score_res.append(np.dot(self.emd[edges[i][0]], self.emd[edges[i][1]]))
        return score_res

    def read_test_edges(self, read_func):
        test_edges = read_func(self.test_filename)
        test_edges_neg = read_func(self.test_neg_filename)

        test_edges.extend(test_edges_neg)  # test_edges????????????????????????????????????????????????????????????

        return test_edges

    def create_labels(self, scores):
        test_label = np.array(scores)

        median = np.median(test_label)  # ???????????????????????????????????????????????????tp+fp==fn+tn
        index_pos = test_label >= median
        index_neg = test_label < median
        test_label[index_pos] = 1
        test_label[index_neg] = 0
        true_label = np.zeros(test_label.shape)

        true_label[0 : len(true_label) // 2] = 1  # ???????????????????????????????????????????????????????????????tp+fn==fp+tn

        return true_label, test_label

    def get_acc_and_macro(self, true_label, test_label):
        """
        ??? tp+fp==fn+tn, tp+fn==fp+tn => tp==tn, fn==fp\n
        ??????accuracy, precision, recall???????????????????????????????????????accuracy??????f1-macro
        """
        # test_eval(true_label, test_label)
        accuracy = accuracy_score(true_label, test_label)
        macro = f1_score(true_label, test_label, average="macro")
        return accuracy, macro


def test_eval(true_label, test_label):
    """???????????????"""
    accuracy = accuracy_score(true_label, test_label)
    macro = f1_score(true_label, test_label, average="macro")

    recall = recall_score(true_label, test_label)
    precision = precision_score(true_label, test_label)
    print("acc: {}, precision: {}, recall: {}".format(accuracy, precision, recall))

    """
    tp ????????????????????? 1,1
    fp ????????????????????? 0,1
    fn ????????????????????? 1,0
    tn ????????????????????? 0,0
    """
    tp = len(np.argwhere(true_label + test_label == 2))
    fn = len(np.argwhere(true_label - test_label == -1))
    fp = len(np.argwhere(true_label - test_label == 1))
    tn = len(np.argwhere(true_label + test_label == 0))
    print("tp: {}, fn: {}, fp: {}, tn: {}".format(tp, fn, fp, tn))
    """
    accuracy, precision, recall???????????????????????????tp==tn???fn==fp
    """
    print((tp + tn) / (tp + tn + fp + fn), tp / (tp + fp), tp / (tp + fn))
