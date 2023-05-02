import plotly.express as px
import plotly.graph_objects as go
from DatabaseReader import DataReader
from ML_Eval import IGFeatureSelector
from Analysis import AnalysisDashBoard
from os import chdir

if __name__ == "__main__":
    # change the directory to project
    chdir('../')
    # creating database table to query from
    table_name = "session_tbl"
    DataReader_obj = DataReader(tbl_name=table_name)

    # calculate Information gain for each column as a feature
    query = f"select * from {table_name}"
    total_table = DataReader_obj.execute_query(query=query)

    IG_feature_selector = IGFeatureSelector().calc_information_gain()

    IG_table_layout = go.Layout(
        title=dict(text="Information Gain/Cardinality Score table")
    )
    IG_table = go.Figure(data=[go.Table(
        header=dict(values=list(IG_feature_selector.columns)),
        cells=dict(values=[IG_feature_selector[name] for name in IG_feature_selector.columns]),

    )], layout=IG_table_layout)

    target_column = total_table["install"]
    """by activating each column, related figure will be added to the final report"""
    categorical_columns = [
        # Location related
        # 'GEO_COUNTRY',
        # 'GEO_CITY',
        'GEO_REGION',
        # 'LANGUAGE',
        # Device related
        'DEVICE_MODEL',
        'DEVICE_OS_VERSION',
        'DEVICE_OS_MINOR',
        'DEVICE_TYPE',
        # Video Aspects
        'VIDEO_PLAYER_SIZE',
        'VIDEO_ASPECT_RATIO',
        # Connection type
        'CONNECTION',
        # Inventory
        # 'inventory_creative_type',
        'INVENTORY_CATEGORIES',
        # IDs
        # 'anonymous_IFA',
        # 'anonymous_TAG_ID',
        'anonymous_APP_BUNDLE',
        'anonymous_EXCHANGE',
        # 'lineitem_id',
        # Auction type
        'AUCTION_TYPE',
        # date related
        'HOUR_INT',
        'DAY_OF_WEEK',
        # 'DATE',
        'date_bid',
        # 'DATETIME',
        # 'HOUR_DECIMAL',
        # Is Rewarded
        'VIDEO_REWARDED'
    ]

    column_list = ['NORMALIZED_BID_FLOOR',
                   'DAY_OF_WEEK',
                   # 'HOUR_DECIMAL',
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
                   # 'lineitem_id',
                   'bid_price',
                   'date_bid',
                   'device_disk_space',
                   'inventory_creative_type',
                   # 'DATE',
                   'HOUR_INT',
                   'imp'
                   'ression_price',
                   'anonymous_IFA',
                   'anonymous_TAG_ID',
                   'anonymous_APP_BUNDLE',
                   'anonymous_EXCHANGE']

    num_columns = [x for x in column_list if x not in categorical_columns]

    IG_cardinality_figure = px.scatter(IG_feature_selector,
                                       x="IG_percentage",
                                       y="Cardinality",
                                       text="Feature")

    IG_cardinality_figure.update_traces(mode='markers', marker_line_width=2, marker_size=15)
    IG_cardinality_figure.update_layout(title='Cardinality & Information Gain Matrix',
                                        yaxis_zeroline=False, xaxis_zeroline=False)

    print("creating treemap")
    Analysis_obj = AnalysisDashBoard(table_name=table_name)

    # here we can create tree maps(it creates a summary for any given columns)
    # this can be created for any given set columns.
    device_treemap = Analysis_obj.create_treemap(data_reader_object=DataReader_obj,
                                                 col_name_list=['DEVICE_TYPE', 'CONNECTION'],
                                                 aggregation_col="count_install",
                                                 title="Number of Installations based on Device/Model/Connection")

    Auction_treemap = Analysis_obj.create_treemap(data_reader_object=DataReader_obj,
                                                  col_name_list=['AUCTION_TYPE',
                                                                 'INVENTORY_CATEGORIES',
                                                                 'inventory_creative_type'],
                                                  aggregation_col="count_install",
                                                  title="Number of Installations based on Auction/Inventory")

    date_treemap = Analysis_obj.create_treemap(data_reader_object=DataReader_obj,
                                               col_name_list=["DAY_OF_WEEK",
                                                              'HOUR_INT'],
                                               aggregation_col="count_install",
                                               title="Number of Installations based on Day_of_week/Hour:24")

    print("created treemap")

    print("create Report")
    shapes_to_browser = dict()
    shapes_to_browser["IG_table"] = IG_table
    shapes_to_browser["IG_Figure"] = IG_cardinality_figure
    shapes_to_browser["Device_treemap"] = device_treemap
    shapes_to_browser["Auction_treemap"] = Auction_treemap
    shapes_to_browser["Date_treemap"] = date_treemap

    # creating bar charts
    for x in categorical_columns:
        shapes_to_browser[x] = Analysis_obj.performance_figures(DataReader_obj, x)

    # sending bar charts to HTML file
    with open(f'Report_Figures_Verve_Group.html', 'w') as f:
        for shape, obj in shapes_to_browser.items():
            f.write(obj.to_html(full_html=False, include_plotlyjs='cdn'))



