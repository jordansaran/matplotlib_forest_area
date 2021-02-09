import json

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


class ForestAreaLand:

    _list_lines = []
    _list_country_name = []
    _list_columns_years = []
    _list_interval_years = []
    _fig = None
    _ax = None
    _ly = None
    _lx = None
    _txt = None
    _list_tuple_data = []
    _list_annotate = []
    horizontal_line = None
    vertical_line = None

    def __init__(self):
        mpl.use('macosx')
        df_forests = pd.read_csv("dataset_forest_land_area.csv", skiprows=4)
        df_forests.drop(columns=['Unnamed: 65', 'Country Code', 'Indicator Name', 'Indicator Code'], inplace=True)
        df_forests.fillna(value=0, inplace=True)
        df_forests.set_index('Country Name', inplace=True)
        df_forests = df_forests[df_forests.index.isin(values=['Brazil', 'United States', 'China', 'India'], level=0)]
        df_forests_t = df_forests.T
        self._df_forest = df_forests_t[(df_forests_t.T != 0).any()].T

    def __creating_lists(self):
        self._list_columns_years = self._df_forest.columns.tolist()
        self._list_country_name = self._df_forest.index.tolist()
        if len(self._list_columns_years) != 0:
            self._list_interval_years = np.arange(int(self._list_columns_years[0]),
                                                  int(self._list_columns_years[-1]), 5).astype('str')
        self.__creating_list_tuple()

    def __creating_lines_plot(self):
        for country_name in self._list_country_name:
            df_by_country = self._df_forest.filter(like=country_name, axis=0)
            line, = self._ax.plot(self._list_columns_years, df_by_country.values[0], '-o')
            self._list_lines.append(line)

    def __creating_subplot(self):
        try:
            self._fig, self._ax = plt.subplots()
            return True
        except BaseException as be:
            print(be)
            return False

    def __configurating_plot(self):
        self._ax.set_xticks(self._list_interval_years)
        self._ax.legend(tuple(self._list_lines), tuple(self._list_country_name),
                        loc='upper right',  bbox_to_anchor=(1, 1.15),
                        ncol=len(self._list_country_name))
        self._ax.set_xlabel('Years', fontsize=14)
        self._ax.set_ylabel('Forest area (% of land area)', fontsize=14)
        self._fig.suptitle('Comparison of forest land occupation')
        self._fig.tight_layout()

    def __create_interactivity(self):
        self._fig.canvas.mpl_connect('motion_notify_event', self.mouse_move)

    def mouse_move(self, event):
        x, y = event.xdata, event.ydata
        self.horizontal_line.set_ydata(y)
        self.vertical_line.set_xdata(x)
        self.set_cross_hair_visible(True)
        if not event.inaxes:
            # need_redraw = self.set_cross_hair_visible(False)
            # if need_redraw:
            #     self._ax.figure.canvas.draw()
            return
        plot_year = self._list_columns_years[int(x) if int(x) > 0 and x <= len(self._list_columns_years) else 0]
        value_forest = round(y, 1)
        if 0 <= int(x) <= len(self._list_columns_years):
            tuple_x_y = tuple([plot_year, value_forest])
        else:
            tuple_x_y = None
        if tuple_x_y is not None:
            if tuple_x_y in self._list_tuple_data:
                self.__plot_annotate(x, y, plot_year, value_forest)
        self._ax.figure.canvas.draw()

    def set_cross_hair_visible(self, visible):
        need_redraw = self.horizontal_line.get_visible() != visible
        self.horizontal_line.set_visible(visible)
        self.vertical_line.set_visible(visible)
        return need_redraw

    def __plot_annotate(self, x, y, plot_year, value_forest) -> bool:
        bbox = dict(boxstyle="round", fc="0.8")
        if len(self._list_annotate) == 0:
            country_name = self.__get_country_name(plot_year, value_forest)
            value_indice = self.__get_indice_by_year(country_name, plot_year)
            self._list_annotate.append(self._ax.annotate("Country: {} \n "
                                                         "Forest area (% of land area) = {}% \n"
                                                         "Indice(Up/Down) by last year = {}%".format(country_name,
                                                                                                     round(y, 2),
                                                                                                     round(value_indice,
                                                                                                           2)),
                                                         (x - 1, y + 2), bbox=bbox))
            return True
        elif len(self._list_annotate) > 0:
            self._list_annotate[0].remove()
            self._list_annotate.clear()
            return False

    def __get_indice_by_year(self, country_name, year):
        if int(self._list_columns_years[0]) == int(year):
            return 0
        else:
            list_values_by_year_on_country = self._df_forest.filter(like=country_name, axis=0).filter(
                items=np.arange(int(year) - 1, int(year) + 1, 1).astype('str')).values.tolist()[0]
        return round(((list_values_by_year_on_country[1] - list_values_by_year_on_country[0]) /
                      list_values_by_year_on_country[0]) * 100, 3)

    def __get_country_name(self, plot_year, value):
        json_forest = self.__get_json_df_forest()
        for country_name in self._list_country_name:
            for year in self._list_columns_years:
                if year == plot_year:
                    data = round(json_forest[country_name][year], 1)
                    if value == data:
                        return country_name
                    break
        return None

    def __get_json_df_forest(self):
        return json.loads(self._df_forest.to_json(orient='index'))

    def __creating_list_tuple(self):
        json_forest = self.__get_json_df_forest()
        for country_name in self._list_country_name:
            for year in self._list_columns_years:
                try:
                    self._list_tuple_data.append(tuple([year, round(json_forest[country_name][year], 1)]))
                except KeyError as ke:
                    print(ke)

    def execute(self):
        if self.__creating_subplot():
            self.horizontal_line = self._ax.axhline(color='k', lw=0.8, ls='-')
            self.vertical_line = self._ax.axvline(color='k', lw=0.8, ls='-')
            self.__creating_lists()
            self.__creating_lines_plot()
            self.__configurating_plot()
            self.__create_interactivity()
            plt.grid()
            plt.show()
        else:
            print("Error")


if __name__ == '__main__':
    forest_area_land = ForestAreaLand()
    forest_area_land.execute()
