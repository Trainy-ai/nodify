// @ts-nocheck
import "./ProgressView.css"
import { useFetch, useAsync } from "react-async"
import { useState, useEffect } from 'react'
import Plot from 'react-plotly.js';

const Start2Start = () => {
    const [plotInput, setPlotInput] = useState([]);

    const fetchData = async ({ setPlotInput }) => {
        const response = await fetch(`./progress_start2start`, {
            headers: { accept: "application/json" },
        })

        if (!response.ok) throw new Error(response.status)
        var out = await response.json();
        setPlotInput(out);
        return response;
    }
    fetchData({ setPlotInput });
    return (
        <>
            <Plot data={plotInput.data} layout={plotInput.layout} />
        </>
    );
};

const Start2End = () => {
    const [plotInput, setPlotInput] = useState([]);

    const fetchData = async ({ setPlotInput }) => {
        const response = await fetch(`./progress_start2end`, {
            headers: { accept: "application/json" },
        })

        if (!response.ok) throw new Error(response.status)
        var out = await response.json();
        setPlotInput(out);
        return response;
    }
    fetchData({ setPlotInput });
    return (
        <>
            <Plot data={plotInput.data} layout={plotInput.layout} />
        </>
    );
};

const ProgressView = ({ menu }) => {
    return (
        <>
            <Start2Start />
            <Start2End />
        </>
    );
};

export default ProgressView;