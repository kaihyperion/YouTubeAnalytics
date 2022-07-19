import pandas as pd
import numpy as np

    """Script 3 (Retention Performance)
    Input: Extracted Excel/CSV file 
    or column of elapsed video time ratio and column of reltaive retntion performance
    
    """
    
    # we will first proceed with inputting from excel/csv
    
    data = pd.read_csv('File name here.csv')
    data2 = pd.pivot_table(data, index = 'elapsedVideoTimeRatio', values = 'relativeRetentionPerformance', aggfunc='mean')
    grand_total = np.mean(data2['relativeRetentionPerformance'])