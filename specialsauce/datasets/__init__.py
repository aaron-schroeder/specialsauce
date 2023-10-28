import os

import pandas as pd


def load_ngp_gap():
    """Load and return the NGP / GAP dataset.
    
    Inspired by sklearn's `load_iris()`.
    """
    module_path = os.path.dirname(__file__)
    ngp_gap_csv_filename = os.path.join(module_path, 'data', 'ngp_gap.csv')
    df_adjusted_pace_str = pd.read_csv(ngp_gap_csv_filename, index_col='Grade')
    df_adjusted_pace_td = df_adjusted_pace_str  \
        .applymap(lambda x: f'00:{x}' if not pd.isnull(x) else x)  \
        .applymap(pd.to_timedelta) 
        # .apply(lambda series: series.dt.total_seconds())

    return df_adjusted_pace_td
