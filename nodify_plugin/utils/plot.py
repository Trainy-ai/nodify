# -------------------------------------------------------------------------
# Copyright (c) Trainy, Inc. All rights reserved.
# --------------------------------------------------------------------------

import numpy as np
import pandas as pd

from functools import partial

from hta.utils.utils import merge_kernel_intervals

from nodify_plugin.utils.dataframe import prepare_df
from nodify_plugin.utils.range import (
    subtract_ranges_lists,
    fraction_uncovered,
)


def binned_percent_usage(df, bins=30):
    """
    Computes the percent usage within equally sized time intervals
    for use in heatmap
    """
    df = merge_kernel_intervals(df)
    m, n = len(bins), len(df)
    range_list1 = [(bins[i], bins[i + 1]) for i in range(m - 1)]
    range_list2 = [(df.iloc[i]["ts"], df.iloc[i]["end"]) for i in range(n)]
    non_compute_range = subtract_ranges_lists(range_list1, range_list2)
    compute_fraction = fraction_uncovered(range_list1, non_compute_range)
    return compute_fraction


def heatmap(trace_data, ranks=None, iterations=None, bins=1000, type="compute"):
    """
    Produces a heatmap by rank using trace data
    """
    df = prepare_df(trace_data, ranks=ranks, iterations=iterations)
    start, end = df.ts.min(), (df.ts + df.dur).max()
    bins = np.linspace(start, end, bins)
    symbol_table = trace_data.symbol_table

    s_map = pd.Series(symbol_table.get_sym_id_map())
    if type == "compute":
        non_computer_name_ids = s_map[
            s_map.index.str.startswith("ncclKernel")
            | s_map.index.str.startswith("Memset")
            | s_map.index.str.startswith("Memcpy")
        ].values
        df = df.loc[
            (~df["name"].isin(non_computer_name_ids)) & (df.stream != -1)
        ]  # stream == -1 corresponds to CPU ops
    elif type == "comm":
        comm_ids = s_map[s_map.index.str.startswith("ncclKernel")].values
        df = df.loc[
            (df["name"].isin(comm_ids)) & (df.stream != -1)
        ]  # stream == -1 corresponds to CPU ops
    else:  # memory operations
        mem_ids = s_map[
            s_map.index.str.startswith("Memset") | s_map.index.str.startswith("Memcpy")
        ].values
        df = df.loc[
            (df["name"].isin(mem_ids)) & (df.stream != -1)
        ]  # stream == -1 corresponds to CPU ops
    compute_fraction = partial(binned_percent_usage, bins=bins)
    binned_gpu_util = df.groupby("rank").apply(compute_fraction)
    return binned_gpu_util, bins


def start_delta(df):
    df = df.sort_values(by="ts")
    df["delta"] = df["ts"].diff()
    return df


def time_between_barriers_start(
    trace_data, comm_id="ncclKernel_AllReduce", ranks=None, iterations=None
):
    """
    Returns the time between barrier operations

    comm_id can be {ncclKernel_AllReduce, ncclKernel_AllGather, ncclKernel_ReduceScatter}
    """
    df = prepare_df(trace_data, ranks=ranks, iterations=iterations)
    symbol_table = trace_data.symbol_table

    s_map = pd.Series(symbol_table.get_sym_id_map())
    communication_ids = s_map[s_map.index.str.startswith(comm_id)].values
    comms_df = df.loc[df["name"].isin(communication_ids)]
    return comms_df.groupby("rank").apply(start_delta).reset_index(drop=True)


def start_end_delta(df):
    df = df.sort_values(by="ts")
    df["end"] = df["ts"] + df["dur"]
    df["end"] = df["end"].shift(1)
    df["delta"] = df["ts"] - df["end"]
    return df


def time_between_barriers_start2end(
    trace_data, comm_id="ncclKernel_AllReduce", ranks=None, iterations=None
):
    """
    Returns the time between barrier operations
    """
    df = prepare_df(trace_data, ranks=ranks, iterations=iterations)
    symbol_table = trace_data.symbol_table

    s_map = pd.Series(symbol_table.get_sym_id_map())
    communication_ids = s_map[s_map.index.str.startswith(comm_id)].values
    comms_df = df.loc[df["name"].isin(communication_ids)]
    return comms_df.groupby("rank").apply(start_end_delta).reset_index(drop=True)
