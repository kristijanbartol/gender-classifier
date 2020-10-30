import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import json


if __name__ == '__main__':
    dataset_name = sys.argv[1]
    acc_data = {}
    avgs = {}

    json_names = [x for x in os.listdir('./') if dataset_name in x]
    for json_name in json_names:
        with open(json_name) as fjson:
            report_dict = json.load(fjson)

        acc_dict = report_dict['acc']
        for subset_key in acc_dict:
            if subset_key not in acc_data:
                acc_data[subset_key] = [acc_dict[subset_key]]
            else:
                acc_data[subset_key].append(acc_dict[subset_key])

        for metric_key in report_dict:
            if metric_key not in avgs:
                avgs[metric_key] = [report_dict[metric_key]['all']]
            else:
                avgs[metric_key].append(report_dict[metric_key]['all'])
    
    acc_data = {k: np.array(v, dtype=np.float32) for k, v in acc_data.items()}

    plt.boxplot(acc_data.values())
    plt.xticks(ticks=range(len(data)), labels=acc_data.keys(), 
            rotation=70, ha='left')
    plt.subplots_adjust(bottom=0.22)
    plt.savefig('report_boxplot.png')

    for key in avgs:
        avgs[key] = np.array(avgs[key], dtype=np.float32)
        avgs[key] = np.mean(avgs[key])
        print(f'{key}: {avgs[key]}')

