import numpy as np


class Sample:
    def __init__(self, df_x, df_y, train_ratio):
        self.df_x = df_x
        self.df_y = df_y
        self.ratio = train_ratio
        self.sample_index = self.create_random_list()

    def create_random_list(self):
        train_ratio = self.ratio
        n, _ = np.shape(self.df_x)
        smpl = np.random.rand(n) < train_ratio
        return smpl

    def separate_train_test(self, df):
        train_df = df[self.sample_index]
        test_df = df[~self.sample_index]
        return train_df, test_df

    def get_sample(self):
        train_df, test_df = self.separate_train_test(self.df_x)
        y_df, y_test_df = self.separate_train_test(self.df_y)
        return train_df, y_df, test_df, y_test_df
