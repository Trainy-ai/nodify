# -------------------------------------------------------------------------
# Copyright (c) Trainy, Inc. All rights reserved.
# --------------------------------------------------------------------------
import numpy as np
import pandas as pd
import os
import json

from functools import cache
from datetime import datetime
from hta.trace_analysis import TraceAnalysis

import plotly
import plotly.express as px

from tensorboard.plugins import base_plugin
import werkzeug
from werkzeug import exceptions, wrappers

import socket

## getting the hostname by socket.gethostname() method
hostname = socket.gethostname()

from nodify_plugin.utils.plot import (
    heatmap,
    time_between_barriers_start,
    time_between_barriers_start2end,
)

from posthog import Posthog

posthog = Posthog(
    project_api_key="phc_4UgX80BfVNmYRZ2o3dJLyRMGkv1CxBozPAcPnD29uP4",
    host="https://app.posthog.com",
)

PLUGIN_NAME = "nodify_plugin"


class NodifyPlugin(base_plugin.TBPlugin):
    """Tensoboard plugin for Nodify Profiler"""

    plugin_name = PLUGIN_NAME
    headers = [("X-Content-Type-Options", "nosniff")]

    def __init__(self, context):
        """Instantiates NodifyPlugin.

        Args:
        context: A base_plugin.TBContext instance.
        """
        posthog.capture(
            f"{hash(hostname)}",
            event="nodify launched",
            timestamp=datetime.utcnow(),
        )
        self.data_provider = context.data_provider
        self.logdir = os.path.abspath(context.logdir.rstrip("/"))
        try:
            self.trace_analyzer = TraceAnalysis(trace_dir=self.logdir)
        except ValueError as e:
            print(
                f"An exception occurred loading your trace files. You will not be able to visualize anything: {str(e)}"
            )

    def is_active(self):
        """Returns whether there is relevant data for the plugin to process.

        When there are no runs with greeting data, TensorBoard will hide the
        plugin from the main navigation bar.
        """
        return not self.trace_analyzer is None

    def get_plugin_apps(self):
        return {
            "/index.js": self.static_file_route,
            "/index.html": self.static_file_route,
            "/consistency_AllReduce_start2start_route": self.consistency_AllReduce_start2start_route,
            "/consistency_AllGather_start2start_route": self.consistency_AllGather_start2start_route,
            "/consistency_ReduceScatter_start2start_route": self.consistency_ReduceScatter_start2start_route,
            "/consistency_AllReduce_start2end_route": self.consistency_AllReduce_start2end_route,
            "/consistency_AllGather_start2end_route": self.consistency_AllGather_start2end_route,
            "/consistency_ReduceScatter_start2end_route": self.consistency_ReduceScatter_start2end_route,
            "/kernel": self.kernel_route,
            "/progress_AllReduce_start2start_route": self.progress_AllReduce_start2start_route,
            "/progress_AllGather_start2end_route": self.progress_AllGather_start2end_route,
            "/progress_ReduceScatter_start2start_route": self.progress_ReduceScatter_start2start_route,
            "/progress_AllReduce_start2end_route": self.progress_AllReduce_start2end_route,
            "/progress_AllGather_start2end_route": self.progress_AllGather_start2end_route,
            "/progress_ReduceScatter_start2end_route": self.progress_ReduceScatter_start2end_route,
            "/temporal": self.temporal_breakdown_route,
            "/comm_heat": self.comm_heat_route,
            "/mem_heat": self.mem_heat_route,
            "/util_heat": self.util_heat_route,
            "/comp_comm_overlap": self.compute_communication_overlap_route,
            "/temporal_dev": self.temporal_dev,
            "/idle_time": self.idle_time_route,
            "/num_ranks": self.num_ranks_route,
        }

    def frontend_metadata(self):
        return base_plugin.FrontendMetadata(
            es_module_path="/index.js", tab_name="Nodify Profiler"
        )

    @wrappers.Request.application
    def static_file_route(self, request: werkzeug.Request):
        filename = os.path.basename(request.path)
        extension = os.path.splitext(filename)[1]
        if extension == ".html":
            mimetype = "text/html"
        elif extension == ".css":
            mimetype = "text/css"
        elif extension == ".js":
            mimetype = "application/javascript"
        else:
            mimetype = "application/octet-stream"
        filepath = os.path.join(os.path.dirname(__file__), "static", filename)
        try:
            with open(filepath, "rb") as infile:
                contents = infile.read()
        except IOError:
            raise exceptions.NotFound("404 Not Found")
        return werkzeug.Response(
            contents, content_type=mimetype, headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    def num_ranks_route(self, request: werkzeug.Request):
        num_ranks = len(self.trace_analyzer.t.traces)
        contents = json.dumps({"num_ranks": num_ranks})
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    def idle_time_route(self, request: werkzeug.Request):
        rank = request.args.get("rank")
        pct = request.args.get("visualizePct")
        pct_bool = pct == "true"

        idle_time_df = self.trace_analyzer.get_idle_time_breakdown(
            ranks=[int(rank)], visualize=False, visualize_pctg=pct_bool
        )[0]
        idle_time_df["stream"] = idle_time_df.stream.astype(str)
        ycol = "idle_time_ratio" if pct_bool else "idle_time"

        fig = px.bar(
            idle_time_df,
            x="stream",
            y=ycol,
            color="idle_category",
            hover_data=["idle_time", "idle_time_ratio"],
            title=f"Idle time breakdown on rank {rank} per CUDA stream",
        )

        if pct_bool:
            fig.update_layout(
                yaxis_tickformat=".2%",
                yaxis_title="Percentage",
                legend_title="Idle Time Breakdown",
            )
        else:
            fig.update_layout(
                yaxis_title="Idle time (us)", legend_title="Idle Time Breakdown"
            )

        contents = plotly.io.to_json(fig)
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    def temporal_dev(self, request: werkzeug.Request):
        del request  # unused
        time_spent_df = self.trace_analyzer.get_temporal_breakdown(visualize=False)
        contents = time_spent_df.to_json()
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    @cache
    def temporal_breakdown_route(self, request: werkzeug.Request):
        del request  # unused
        time_spent_df = self.trace_analyzer.get_temporal_breakdown(visualize=False)
        fig = px.bar(
            time_spent_df,
            x="rank",
            y=["idle_time_pctg", "compute_time_pctg", "non_compute_time_pctg"],
            title="Temporal breakdown across ranks",
            labels={"rank": "Rank"},
        )
        fig.update_layout(
            yaxis_tickformat=".%",
            yaxis_title="Percentage",
            legend_title="Time Breakdown",
        )
        contents = plotly.io.to_json(fig)
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    @cache
    def kernel_route(self, request: werkzeug.Request):
        # TODO: Refactor this to split the dataframe logic from the plotting logic for the later plots
        del request  # unused
        (
            kernel_type_df,
            kernel_metrics_df,
        ) = self.trace_analyzer.get_gpu_kernel_breakdown(visualize=False)
        non_zero_kernel_df = kernel_type_df[(kernel_type_df["percentage"] > 0)]

        fig = px.pie(
            non_zero_kernel_df,
            values="percentage",
            names="kernel_type",
            height=500,
            title="Kernel Type Percentage Across All Ranks",
        )
        fig.update_layout(
            margin=dict(l=50, r=50, b=50, t=50),
            showlegend=True,
            legend=dict(yanchor="bottom", y=-0.4, xanchor="left", x=0),
        )

        contents = plotly.io.to_json(fig)
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    def consistency_AllReduce_start2start_route(self, request: werkzeug.Request):
        del request

        df = time_between_barriers_start(
            self.trace_analyzer.t, comm_id="ncclKernel_AllReduce"
        )
        fig = px.box(
            df.dropna(),
            x="rank",
            y="delta",
            color="iteration",
            title="time between ncclKernel_AllReduce starts",
            labels={"delta": "time delta (ns)"},
        )
        contents = plotly.io.to_json(fig)
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    def consistency_ReduceScatter_start2start_route(self, request: werkzeug.Request):
        del request

        df = time_between_barriers_start(
            self.trace_analyzer.t, comm_id="ncclKernel_ReduceScatter"
        )
        fig = px.box(
            df.dropna(),
            x="rank",
            y="delta",
            color="iteration",
            title="time between ncclKernel_ReduceScatter starts",
            labels={"delta": "time delta (ns)"},
        )
        contents = plotly.io.to_json(fig)
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    def consistency_AllGather_start2start_route(self, request: werkzeug.Request):
        del request

        df = time_between_barriers_start(
            self.trace_analyzer.t, comm_id="ncclKernel_AllGather"
        )
        fig = px.box(
            df.dropna(),
            x="rank",
            y="delta",
            color="iteration",
            title="time between ncclKernel_AllGather starts",
            labels={"delta": "time delta (ns)"},
        )
        contents = plotly.io.to_json(fig)
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    def consistency_AllReduce_start2end_route(self, request: werkzeug.Request):
        del request

        df = time_between_barriers_start2end(
            self.trace_analyzer.t, comm_id="ncclKernel_AllReduce"
        )
        fig = px.box(
            df.dropna(),
            x="rank",
            y="delta",
            color="iteration",
            title="time between ncclKernel_AllReduce starts",
            labels={"delta": "time delta (ns)"},
        )
        contents = plotly.io.to_json(fig)
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    def consistency_ReduceScatter_start2end_route(self, request: werkzeug.Request):
        del request

        df = time_between_barriers_start2end(
            self.trace_analyzer.t, comm_id="ncclKernel_ReduceScatter"
        )
        fig = px.box(
            df.dropna(),
            x="rank",
            y="delta",
            color="iteration",
            title="time between ncclKernel_ReduceScatter starts",
            labels={"delta": "time delta (ns)"},
        )
        contents = plotly.io.to_json(fig)
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    def consistency_AllGather_start2end_route(self, request: werkzeug.Request):
        del request

        df = time_between_barriers_start2end(
            self.trace_analyzer.t, comm_id="ncclKernel_AllGather"
        )
        fig = px.box(
            df.dropna(),
            x="rank",
            y="delta",
            color="iteration",
            title="time between ncclKernel_AllGather starts",
            labels={"delta": "time delta (ns)"},
        )
        contents = plotly.io.to_json(fig)
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    ################################
    @wrappers.Request.application
    def progress_AllReduce_start2start_route(self, request: werkzeug.Request):
        del request

        df = time_between_barriers_start(
            self.trace_analyzer.t, comm_id="ncclKernel_AllReduce"
        )
        fig = px.box(
            df.dropna(),
            x="iteration",
            y="delta",
            color="rank",
            title="time between ncclKernel_AllReduce starts",
            labels={"delta": "time delta (ns)"},
        )
        contents = plotly.io.to_json(fig)
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    def progress_ReduceScatter_start2start_route(self, request: werkzeug.Request):
        del request

        df = time_between_barriers_start(
            self.trace_analyzer.t, comm_id="ncclKernel_ReduceScatter"
        )
        fig = px.box(
            df.dropna(),
            x="iteration",
            y="delta",
            color="rank",
            title="time between ncclKernel_ReduceScatter starts",
            labels={"delta": "time delta (ns)"},
        )
        contents = plotly.io.to_json(fig)
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    def progress_AllGather_start2start_route(self, request: werkzeug.Request):
        del request

        df = time_between_barriers_start(
            self.trace_analyzer.t, comm_id="ncclKernel_AllGather"
        )
        fig = px.box(
            df.dropna(),
            x="iteration",
            y="delta",
            color="rank",
            title="time between ncclKernel_AllGather starts",
            labels={"delta": "time delta (ns)"},
        )
        contents = plotly.io.to_json(fig)
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    def progress_AllReduce_start2end_route(self, request: werkzeug.Request):
        del request

        df = time_between_barriers_start2end(
            self.trace_analyzer.t, comm_id="ncclKernel_AllReduce"
        )
        fig = px.box(
            df.dropna(),
            x="iteration",
            y="delta",
            color="rank",
            title="time between ncclKernel_AllReduce starts",
            labels={"delta": "time delta (ns)"},
        )
        contents = plotly.io.to_json(fig)
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    def progress_ReduceScatter_start2end_route(self, request: werkzeug.Request):
        del request

        df = time_between_barriers_start2end(
            self.trace_analyzer.t, comm_id="ncclKernel_ReduceScatter"
        )
        fig = px.box(
            df.dropna(),
            x="iteration",
            y="delta",
            color="rank",
            title="time between ncclKernel_ReduceScatter starts",
            labels={"delta": "time delta (ns)"},
        )
        contents = plotly.io.to_json(fig)
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    def progress_AllGather_start2end_route(self, request: werkzeug.Request):
        del request

        df = time_between_barriers_start2end(
            self.trace_analyzer.t, comm_id="ncclKernel_AllGather"
        )
        fig = px.box(
            df.dropna(),
            x="iteration",
            y="delta",
            color="ranks",
            title="time between ncclKernel_AllGather starts",
            labels={"delta": "time delta (ns)"},
        )
        contents = plotly.io.to_json(fig)
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    def util_heat_route(self, request: werkzeug.Request):
        del request  # unused

        fraction, bins = heatmap(self.trace_analyzer.t, bins=30, type="compute")
        fraction = fraction.reset_index().rename(columns={0: "gpu_util"})
        fig = px.imshow(
            list(fraction["gpu_util"].values),
            labels=dict(x="Time (us)", y="rank", color="GPU Util"),
            y=fraction["rank"],
            title="% Time Computation",
        )

        fig.update_xaxes(
            tickangle=90,
            tickmode="array",
            tickvals=np.arange(len(bins)),
            ticktext=[d.strftime("%f") for d in pd.to_datetime(bins[:-1])],
        )

        contents = plotly.io.to_json(fig)
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    def comm_heat_route(self, request: werkzeug.Request):
        del request  # unused

        fraction, bins = heatmap(self.trace_analyzer.t, bins=30, type="comm")
        fraction = fraction.reset_index().rename(columns={0: "gpu_comm"})
        fig = px.imshow(
            list(fraction["gpu_comm"].values),
            labels=dict(x="Time (us)", y="rank", color="GPU Comm"),
            y=fraction["rank"],
            title="% Time Communication",
        )

        fig.update_xaxes(
            tickangle=90,
            tickmode="array",
            tickvals=np.arange(len(bins)),
            ticktext=[d.strftime("%f") for d in pd.to_datetime(bins[:-1])],
        )

        contents = plotly.io.to_json(fig)
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    def mem_heat_route(self, request: werkzeug.Request):
        del request  # unused

        fraction, bins = heatmap(self.trace_analyzer.t, bins=30, type="mem")
        fraction = fraction.reset_index().rename(columns={0: "gpu_mem"})
        fig = px.imshow(
            list(fraction["gpu_mem"].values),
            labels=dict(x="Time (us)", y="rank", color="GPU Mem"),
            y=fraction["rank"],
            title="% Time Memory",
        )

        fig.update_xaxes(
            tickangle=90,
            tickmode="array",
            tickvals=np.arange(len(bins)),
            ticktext=[d.strftime("%f") for d in pd.to_datetime(bins[:-1])],
        )

        contents = plotly.io.to_json(fig)
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )

    @wrappers.Request.application
    @cache
    def compute_communication_overlap_route(self, request: werkzeug.Request):
        del request

        result_df = self.trace_analyzer.get_comm_comp_overlap(visualize=False)

        fig = px.bar(
            result_df,
            x="rank",
            y="comp_comm_overlap_pctg",
            title="Computation-Communication Overlap",
            labels={
                "rank": "Rank",
                "comp_comm_overlap_pctg": "Computation-Communication Overlap Percentage",
            },
        )

        contents = plotly.io.to_json(fig)
        return werkzeug.Response(
            contents, content_type="application/json", headers=NodifyPlugin.headers
        )


if __name__ == "__main__":
    print("hello")
