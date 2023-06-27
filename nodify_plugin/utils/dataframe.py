# -------------------------------------------------------------------------
# Copyright (c) Trainy, Inc. All rights reserved.
# --------------------------------------------------------------------------

import pandas as pd

def prepare_df(trace_data, ranks=None, iterations=None):
    """
    Creates dataframe of symbol table across all ranks and iterations
    queried. Defaults to all ranks and iterations
    """
    _ranks = list(trace_data.get_all_traces().keys())
    df = pd.concat(
        [trace_data.get_trace(r) for r in _ranks],
        axis=0,
        keys=_ranks,
        names=["rank", "idx"],
    ).reset_index()
    if ranks:
        df = df[df.ranks.isin(ranks)]
    if iterations:
        df = df[df.iteration.isin(iterations)]
    return df
