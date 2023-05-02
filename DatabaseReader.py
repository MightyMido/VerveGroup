import pandas as pd
import sqlite3 as db
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline


class DataReader:
    def __init__(self, tbl_name="session_tbl", csv_dir="Data/video_campaign.csv"):
        self.table_name = tbl_name
        self.csv_dir = csv_dir
        self.conn = db.connect(':memory:')
        self.convert_table()
        self.categorical_columns = [
            # Location related
            'GEO_CITY',
            'GEO_REGION',
            'LANGUAGE',
            # Device related
            'DEVICE_MODEL',
            'DEVICE_OS_VERSION',
            'DEVICE_OS_MINOR',
            'DEVICE_TYPE',
            # Video specs
            'VIDEO_PLAYER_SIZE',
            'VIDEO_ASPECT_RATIO',
            # Connection type
            'CONNECTION',
            # Inventory
            'inventory_creative_type',
            'INVENTORY_CATEGORIES',
            # IDs
            'anonymous_IFA',
            'anonymous_TAG_ID',
            'anonymous_APP_BUNDLE',
            'anonymous_EXCHANGE',
            'lineitem_id',
            # Auction type
            'AUCTION_TYPE',
            # date related
            'HOUR_INT',
            'DAY_OF_WEEK',
            'DATETIME',
            'HOUR_DECIMAL',
            # Is Rewarded
            'VIDEO_REWARDED'
        ]

        self.column_list = ['DATETIME',
                            'NORMALIZED_BID_FLOOR',
                            'DAY_OF_WEEK',
                            'HOUR_DECIMAL',
                            'SESSION_DEPTH',
                            'CAMPAIGN_IMPRESSION_COUNT',
                            'CREATIVE_IMPRESSION_COUNT',
                            'VIDEO_REWARDED',
                            'GEO_CITY',
                            'GEO_REGION',
                            'GEO_COUNTRY',
                            'INVENTORY_CATEGORIES',
                            'LANGUAGE',
                            'DEVICE_MODEL',
                            'DEVICE_OS_VERSION',
                            'DEVICE_OS_MINOR',
                            'DEVICE_TYPE',
                            'VIDEO_PLAYER_SIZE',
                            'VIDEO_ASPECT_RATIO',
                            'CONNECTION',
                            'AUCTION_TYPE',
                            'USER_SESSION_DURATION',
                            'lineitem_id',
                            'bid_price',
                            'date_bid',
                            'device_disk_space',
                            'inventory_creative_type',
                            'DATE',
                            'HOUR_INT',
                            'impression_price',
                            'anonymous_IFA',
                            'anonymous_TAG_ID',
                            'anonymous_APP_BUNDLE',
                            'anonymous_EXCHANGE']

        self.value_columns = [x for x in self.column_list if x not in self.categorical_columns]
        self.target_column = "install"

    def convert_table(self):
        dt = pd.read_csv(self.csv_dir)
        dt.to_sql(self.table_name, self.conn, index=False)
        pass

    def execute_query(self, query):
        pandas_dataframe = pd.read_sql(query, con=self.conn)
        return pandas_dataframe

    def create_pipline(self):
        col_transformer = ColumnTransformer([('one_hot_encoder', OneHotEncoder(), self.categorical_columns)])
        pipeline = Pipeline([('column_transformer', col_transformer)])
        df = self.execute_query(f"select * from {self.table_name}")
        encoded_df = pipeline.fit_transform(df)
        return encoded_df
