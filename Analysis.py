import plotly.express as px
import plotly.graph_objects as go


class AnalysisDashBoard:
    def __init__(self, table_name=""):
        self.metric_list = ["total_imp_price_install",
                            "count_install",
                            "price_per_install",
                            "total_imp_price_creative",
                            "count_creative_impression",
                            "price_per_creative",
                            "install_per_impression"]
        self.tbl_name = table_name

        self.install_query = ("select " +
                              "{column_name_list} , " +
                              "sum(impression_price) / 1000000 as total_imp_price_install, " +
                              "sum(install) as count_install , " +
                              "coalesce(sum(impression_price)/(sum(install) * 1000000),0) as price_per_install" +
                              f" from {self.tbl_name} "
                              " group by {column_name_list}")

        self.creative_query = ("select " +
                               "{column_name_list} , " +
                               "sum(impression_price) / 1000000 as total_imp_price_creative, " +
                               "sum(CREATIVE_IMPRESSION_COUNT) as count_creative_impression , " +
                               "coalesce(sum(impression_price)/" +
                               "(sum(CREATIVE_IMPRESSION_COUNT) * 1000000),0) as price_per_creative " +
                               f" from {self.tbl_name} where CREATIVE_IMPRESSION_COUNT > 0 " +
                               " group by {column_name_list} "
                               )
        pass

    def create_metric_fig(self,
                          performance_tbl,
                          prediction_column='anonymous_APP_BUNDLE',
                          col_list=None):
        # Convert variable names to use them in text
        if col_list is None:
            col_list = self.metric_list

        prediction_column_name = prediction_column.replace('_', ' ')

        # extract unique values to generate different shapes
        variable_values = col_list
        variable_values = [str(v) for v in variable_values]

        # add trend line to data
        variable_values.append("Average Booking Probability")

        # separating data for creating different shapes
        filter_on_variable = dict()

        # create a list for filtered data
        visibility_list = [True for _ in variable_values]

        # create shapes to see all together
        filter_on_variable['All'] = performance_tbl
        filter_variable_list = [dict(label="Click to change Metric",
                                     method="update",
                                     args=[
                                         {"visible": visibility_list},
                                         {"title": " Performance Metrics for each APP_ID"}
                                     ]
                                     )
                                ]
        fig = go.Figure()

        i = 0

        # adding shapes to figure object
        for var in col_list:
            perf_matrix = performance_tbl[[var, prediction_column]].sort_values(var, ascending=False)
            filter_on_variable[var] = perf_matrix
            trace_obj = go.Bar(x=perf_matrix[prediction_column],
                               y=perf_matrix[var],
                               # mode='lines+markers',
                               name=f"{var}")

            fig.add_trace(trace_obj)

            visibility_list = [False for _ in variable_values]
            visibility_list[i] = True
            name = var.replace("_", " ")
            new_filter_dict = dict(label=f"{str(var)}",
                                   method="update",
                                   args=[{"visible": visibility_list},
                                         {
                                             "title": f"{prediction_column} performance for Metric : ({name})"
                                         }
                                         ])

            filter_variable_list.append(new_filter_dict)
            i += 1

        # adding the filters to the figure
        buttons_lst = list(filter_variable_list)

        # legend properties
        legend_properties = dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1
        )
        # adding
        fig.update_layout(
            updatemenus=[dict(active=0, buttons=buttons_lst, )],
            xaxis_title=prediction_column_name,
            yaxis_title="Value",
            legend=legend_properties
        )
        return fig

    def performance_figures(self, data_reader_object, column_name):
        install_query = self.install_query.format(column_name_list=column_name)

        creative_query = self.creative_query.format(column_name_list=column_name)

        install_result = data_reader_object.execute_query(install_query)
        creative_result = data_reader_object.execute_query(creative_query)

        performance_result = install_result.merge(creative_result,
                                                  how="left",
                                                  on=column_name)

        performance_result["install_per_impression"] = performance_result["count_install"] \
                                                       / performance_result["count_creative_impression"]

        performance_result = performance_result.fillna(0)
        fig = self.create_metric_fig(performance_tbl=performance_result, prediction_column=column_name)
        return fig

    def create_treemap(self, data_reader_object, col_name_list, aggregation_col, title):
        col_string = ', '.join(col_name_list)
        treemap_query = self.install_query.format(column_name_list=col_string)

        result_df = data_reader_object.execute_query(treemap_query)
        result_df = result_df.fillna(0)
        fig = px.treemap(result_df, path=col_name_list, values=aggregation_col)
        fig.update_layout(title=title)
        return fig
