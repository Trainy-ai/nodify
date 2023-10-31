// @ts-nocheck
import "./ProgressView.css"
import { useFetch, useAsync } from "react-async"
import { useState, useEffect } from 'react'
import Plot from 'react-plotly.js';

const fetchData = async ({ setPlotInput }, url) => {
    const response = await fetch(url, {
        headers: { accept: "application/json" },
    })

    if (!response.ok) throw new Error(response.status)
    var out = await response.json();
    setPlotInput(out);
    return response;
}

const BoxPlot = ({ url }) => {
    const [plotInput, setPlotInput] = useState([]);
    fetchData({ setPlotInput }, url);
    return (
        <>
            <Plot data={plotInput.data} layout={plotInput.layout} />
        </>
    )
}

const ProgressView = ({ menu }) => {
    return (
        <>
            <BoxPlot url="./progress_AllReduce_start2start_route" />
            <BoxPlot url="./progress_AllReduce_start2end_route" />
            <BoxPlot url="./progress_AllGather_start2start_route" />
            <BoxPlot url="./progress_AllGather_start2end_route" />
            <BoxPlot url="./progress_ReduceScatter_start2start_route" />
            <BoxPlot url="./progress_ReduceScatter_start2end_route" />
        </>
    );
};

export default ProgressView;