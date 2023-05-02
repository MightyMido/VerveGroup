from DatabaseReader import DataReader
from math import log2
import pandas as pd


class IGFeatureSelector(DataReader):
    """ finding out which column has the better Ability to be used as Feature """

    def __init__(self, tbl_name="session_tbl", csv_dir="Data/video_campaign.csv"):
        super().__init__()
        self.query = ("select "
                      "{col}, " +
                      "sum(impression_price) / 1000000 as total_install_price, " +
                      "sum(install) as count_install , " +
                      "count(1) as cnt_total," +
                      "cast(count(1) as float) / cast({count_sessions} as float) as prob_{col}," +
                      "sum(install) / count(1) as installation_probability," +
                      "coalesce(sum(impression_price)/(sum(install) * 1000000),0) as price_per_install," +
                      " coalesce(-ln(cast(sum(install) as float) / cast(count(1) as float)) * " +
                      " cast(sum(install) as float) / cast(count(1) as float),0) as Entropy " +
                      " from {table_name} group by {col}")
        self.table_name = tbl_name
        self.csv_dir = csv_dir

    def calc_total_entropy(self):
        """Compute the entropy of a target variable."""
        # query definitions
        count_sessions_query = f"select count(1) cnt_sessions from {self.table_name}"
        count_installs_query = f"select sum(install) sum_install from {self.table_name}"
        # extract values
        count_sess = self.execute_query(query=count_sessions_query)["cnt_sessions"].values[0]
        count_install = self.execute_query(query=count_installs_query)["sum_install"].values[0]
        # calculate metrics
        average_install = count_install / count_sess
        average_not_install = 1 - average_install
        avg_1 = -average_install * log2(average_install)
        avg_2 = -average_not_install * log2(average_not_install)
        ttl_entropy = avg_1 + avg_2
        return ttl_entropy, count_install, count_sess

    def calc_information_gain(self):
        """Compute information gain of each column as a feature."""
        total_entropy, count_install, count_sessions = self.calc_total_entropy()
        count_rows_query = f"select count(1) from {self.table_name}"
        count_rows = self.execute_query(count_rows_query).values[0][0]
        cnt_query = "select count(distinct {col}) from {table_name}"
        ig_list = []
        for col in self.column_list:
            granularity_query = cnt_query.format(col=col, table_name=self.table_name)
            cnt_granularity = (self.execute_query(granularity_query).values[0][0] * 100) / count_rows
            price_per_install_query = self.query.format(col=col,
                                                        table_name=self.table_name,
                                                        count_sessions=count_sessions)
            df = self.execute_query(price_per_install_query)
            df["weighted_entropy"] = df[f"prob_{col}"] * df["Entropy"]
            weighted_entropy = df["weighted_entropy"].sum()
            ig_list.append((col,
                            total_entropy - weighted_entropy,
                            (total_entropy - weighted_entropy) * 100 / total_entropy,
                            cnt_granularity))
        sorted_list = sorted(ig_list, key=lambda x: x[1], reverse=True)
        ig_df = pd.DataFrame(sorted_list, columns=["Feature", "IG", "IG_percentage", "Cardinality"])
        return ig_df
