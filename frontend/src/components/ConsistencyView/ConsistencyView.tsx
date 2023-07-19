// @ts-nocheck
import "./ConsistencyView.css"
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

const Start2StartAllReduce = ({ menu }, url) => {
    const [plotInput, setPlotInput] = useState([]);
    fetchData({ setPlotInput }, `./consistency_AllReduce_start2start_route`);
    return (
        <>
            <Plot data={plotInput.data} layout={plotInput.layout} />
        </>
    );
};

const Start2EndAllReduce = ({ menu }) => {
    const [plotInput, setPlotInput] = useState([]);
    fetchData({ setPlotInput }, `./consistency_AllReduce_start2end_route`);
    return (
        <>
            <Plot data={plotInput.data} layout={plotInput.layout} />
        </>
    );
};

const Start2StartAllGather = ({ menu }, url) => {
    const [plotInput, setPlotInput] = useState([]);
    fetchData({ setPlotInput }, `./consistency_AllGather_start2start_route`);
    return (
        <>
            <Plot data={plotInput.data} layout={plotInput.layout} />
        </>
    );
};

const Start2EndAllGather = ({ menu }) => {
    const [plotInput, setPlotInput] = useState([]);
    fetchData({ setPlotInput }, `./consistency_AllGather_start2end_route`);
    return (
        <>
            <Plot data={plotInput.data} layout={plotInput.layout} />
        </>
    );
};

const Start2StartReduceScatter = ({ menu }, url) => {
    const [plotInput, setPlotInput] = useState([]);
    fetchData({ setPlotInput }, `./consistency_ReduceScatter_start2start_route`);
    return (
        <>
            <Plot data={plotInput.data} layout={plotInput.layout} />
        </>
    );
};

const Start2EndReduceScatter = ({ menu }) => {
    const [plotInput, setPlotInput] = useState([]);
    fetchData({ setPlotInput }, `./consistency_ReduceScatter_start2end_route`);
    return (
        <>
            <Plot data={plotInput.data} layout={plotInput.layout} />
        </>
    );
};

const ConsistencyView = ({ menu }) => {
    return (
        <>
            <Start2StartAllReduce />
            <Start2EndAllReduce />
            <Start2StartAllGather />
            <Start2EndAllGather />
            <Start2StartReduceScatter />
            <Start2EndReduceScatter />
        </>
    );
};

export default ConsistencyView;