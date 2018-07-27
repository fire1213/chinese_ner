import os
import copy
import codecs


class PrepareTagData(object):
    def __init__(self, conf, mode="train"):
        """
        mode: is what dataset can ben used. can be [train/test/validate]
        :param conf:
        :param mode:
        """
        self.config = conf
        self.mode = mode
        self.vocabDict = self.__load_chinese_vocab()
        self.tagId = self._tag_id()
        self._sourceData = self.__read_dataset()

    @staticmethod
    def __load_chinese_vocab():
        cv = dict()
        with codecs.open(os.path.join(os.path.dirname(os.getcwd()), "data/chinese_vocab.txt"), "r", "utf8") as f:
            for i, line in enumerate(f.readlines()):
                cv[line.strip()] = i
        return cv

    def __read_dataset(self):
        if self.mode == "train":
            dataset_path = os.path.join(os.path.dirname(os.getcwd()), "data/trainset.txt")
        elif self.mode == "test":
            dataset_path = os.path.join(os.path.dirname(os.getcwd()), "data/testset.txt")
        else:
            raise Exception("mode must be in [train/test]")
        if not os.path.exists(dataset_path):
            raise Exception("path [{}] not exists".format(dataset_path))
        with codecs.open(dataset_path, "r", "utf8") as fp:
            while True:
                a_line = fp.readline()
                if a_line:
                    yield a_line.strip()
                else:
                    break

    def _tag_id(self):
        tag_dict = dict()
        for i, v in enumerate(self.config.tag_char.split(",")):
            tag_dict[v] = i
        return tag_dict

    def __is_end_sentence(self, cur):
        if cur.endswith(self.config.dataset_flag):
            return True
        return False

    def __next__(self):
        sentence_lst = []
        count = 0
        try:
            sentence = []
            while count < self.config.batch_size:
                cur = next(self._sourceData)
                if self.__is_end_sentence(cur):
                    count += 1
                    sentence_lst.append(copy.deepcopy(sentence))
                    sentence = []
                else:
                    sentence.append(cur)

        except StopIteration as iter_exception:
            if count == 0:
                raise iter_exception
        deal_sentence_lst = self.__deal_batch_data(sentence_lst)
        input_x, input_y = self.__split_batch_data(deal_sentence_lst)
        return input_x, input_y

    @staticmethod
    def __split_batch_data(sentence_lst):
        inputs_x = []
        inputs_y = []
        for sentence in sentence_lst:
            inputs_x.append([item[0] for item in sentence])
            inputs_y.append([item[1] for item in sentence])
        return inputs_x, inputs_y

    def __deal_batch_data(self, sentence_lst):
        sentence_ids = []
        for sentence in sentence_lst:
            char_ids = []
            for line in sentence:
                line = line.split(" ")
                vocab_id = self.vocabDict.get(line[0], -1)
                if vocab_id == -1:
                    continue
                tag_id = self.tagId.get(line[1], -1)
                if tag_id == -1:
                    continue
                char_ids.append([vocab_id, tag_id])
            sentence_ids.append(char_ids)
        return sentence_ids


if __name__ == "__main__":
    class CFG:
        batch_size = 10
        tag_char = "O,B-S-ORG,I-S-ORG,E-S-ORG"
        dataset_flag = "end"


    cfg = CFG()
    a = PrepareTagData(cfg, "train")
    while True:
        try:
            train_x, train_y = next(a)
            print(train_x)
            print(train_y)
        except Exception as e:
            exit()
