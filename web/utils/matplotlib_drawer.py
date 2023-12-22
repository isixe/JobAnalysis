# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/20 22:43
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : matplotlib drawer

import base64
import matplotlib
from io import BytesIO
import matplotlib.pylab
from wordcloud import WordCloud


class MatplotlibDrawer(object):
    """ Matplotlib drawer tool """

    def __init__(self):
        """ Config init """
        self.plt = matplotlib.pylab
        self.plt.switch_backend('agg')
        self.plt.rcParams['font.size'] = 12
        self.plt.rcParams['font.sans-serif'] = ['SimHei']

    def bar(self, x: list, y: list, title: str, xlabel: str, ylabel: str, legendlabels: list):
        """ Draw bar by plt

        :Arg:
         - x: x axis list
         - y: y axis list
         - title: plt title
         - xlabel: x axis label
         - ylabel: y axis label
         - legendlabels: legend label list
        """
        self.plt.bar(x, y, color='#1f77b4')

        self.plt.title(title, y=1.05)
        self.plt.xlabel(xlabel)
        self.plt.ylabel(ylabel)
        self.plt.legend(legendlabels, loc='upper right')
        self.plt.gca().get_legend().set_bbox_to_anchor((1.0, 1.1))
        self.plt.gca().spines['top'].set_visible(False)
        self.plt.gca().spines['right'].set_visible(False)

        for i in range(len(x)):
            self.plt.annotate(str(y[i]), xy=(x[i], y[i]), ha='center', va='bottom')

        return self.plt

    def pie(self, x: list, labels: list, title: str, legendlabels: list):
        """  Draw pie by plt

        :Arg:
         - x: x axis list
         - labels: the quantity corresponding to x
         - title: plt title
         - legendlabels: legend label list
        """
        fig, ax = self.plt.subplots()
        ax.pie(x,
               labels=labels,
               labeldistance=1.1,
               autopct='%1.1f%%')

        bbox = ax.get_position()
        ax.set_position([bbox.x0 - 0.1, bbox.y0, bbox.width, bbox.height])
        ax.legend(legendlabels, loc='upper right', bbox_to_anchor=(1.35, 1.1))
        self.plt.title(title, y=1.05)
        self.plt.axis('equal')
        return self.plt

    def boxplot(self, x: list, y: list, title: str, xlabel: str, ylabel: str):
        """ Draw boxplot by plt

        :Arg:
         - x: x axis list
         - y: y axis list
         - title: plt title
         - xlabel: x axis label
         - ylabel: y axis label
        """
        self.plt.boxplot(y)
        self.plt.xticks(range(1, len(x) + 1), x)
        self.plt.title(title, y=1.05)
        self.plt.xlabel(xlabel)
        self.plt.ylabel(ylabel)
        self.plt.gca().spines['top'].set_visible(False)
        self.plt.gca().spines['right'].set_visible(False)
        return self.plt

    def scatter(self, x: list, y: list, title: str, xlabel: str, ylabel: str):
        """ Draw scatter by plt

        :Arg:
         - x: x axis list
         - y: y axis list
         - title: plt title
         - xlabel: x axis label
         - ylabel: y axis label
        """
        self.plt.scatter(y,
                         x,
                         c="lightblue",
                         edgecolors="green",
                         s=50)

        self.plt.title(title, y=1.05)
        self.plt.xlabel(xlabel)
        self.plt.ylabel(ylabel)
        self.plt.gca().spines['top'].set_visible(False)
        self.plt.gca().spines['right'].set_visible(False)
        return self.plt

    def plot(self, a: list, b: list, y: list, title: str, xlabel: str, ylabel: str):
        self.plt.plot(y, a, color='green')
        self.plt.plot(y, b)
        averageA = sum(a) / len(a)
        averageB = sum(b) / len(b)
        self.plt.title(title, y=1.05)
        self.plt.xlabel(xlabel)
        self.plt.ylabel(ylabel)
        self.plt.axhline(averageA, color='blue', linestyle='--', label='Average')
        self.plt.axhline(averageB, color='red', linestyle='--', label='Average')
        self.plt.gca().spines['top'].set_visible(False)
        self.plt.gca().spines['right'].set_visible(False)
        return self.plt

    def barh(self, x: list, y: list, title: str, xlabel: str, ylabel: str, legendlabels: list):
        """ Draw barh by plt

        :Arg:
         - x: x axis list
         - y: y axis list
         - title: plt title
         - xlabel: x axis label
         - ylabel: y axis label
        """
        self.plt.barh(y,
                      x,
                      facecolor='tan',
                      height=150,
                      edgecolor='r',
                      alpha=0.6,
                      tick_label=y)

        self.plt.title(title, y=1.05)
        self.plt.xlabel(xlabel)
        self.plt.ylabel(ylabel)
        self.plt.legend(legendlabels, loc='upper right')
        self.plt.gca().spines['top'].set_visible(False)
        self.plt.gca().spines['right'].set_visible(False)
        return self.plt

    def word_cloud(self, text: str, title: str):
        """ Draw barh wordcloud

        :Arg:
         - text:
         - title: plt title
        """
        wordcloud = WordCloud(font_path='/fonts/simkai.ttf',
                              height=800,
                              width=1000,
                              background_color="white").generate(text)

        self.plt.imshow(wordcloud, interpolation='bilinear')
        self.plt.title(title, y=1.05)
        self.plt.axis('off')
        return self.plt

    def generate_base64(self, plt: matplotlib.pylab):
        """ Generate base64 by plt

        :Arg:
         - plt: matplotlib.pylab
        """
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        prefix = 'data:image/png;base64,'
        encoded = prefix + base64.b64encode(buffer.getvalue()).decode()
        self.__close()
        return encoded

    def __close(self):
        """ Cleanning plt figure """

        self.plt.close('all')
