import pandas as pd
import matplotlib.pyplot as plt

import pandas as pd
import matplotlib.pyplot as plt


def plot_similarity_differences(similarities, figsize=(14, 7), title='Differences for Each Date Range', xlabel='Date', ylabel='Difference', legend_title='Date Ranges'):

    # 유사도에서 differences를 추출하여 DataFrame으로 변환
    all_differences = pd.concat([pd.Series(sim['differences'], name=f"Start: {sim['start_date']}, End: {sim['end_date']}") for sim in similarities], axis=1)
    print(all_differences)

    # 차이값 그래프 시각화
    all_differences.plot(figsize=figsize)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(title=legend_title)
    plt.show()
