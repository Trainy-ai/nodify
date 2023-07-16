// @ts-nocheck
import "./TemporalView.css"
import { useFetch, useAsync } from "react-async"
import { useState, useEffect } from 'react'
import Plot from 'react-plotly.js';

const fetchData = async ( {setPlotInput} ) => {
    const response = await fetch(`./temporal_dev`, {
        headers: { accept: "application/json" },
    })
    if (!response.ok) throw new Error(response.status)
    var out = await response.json();
    setPlotInput([out]);
    console.log('inside');
    console.log(response);
    console.log(out);
    console.log(out['idle_time_pctg']);
    return response;
}

const TemporalView = ({ menu }) => {
    const [plotInput, setPlotInput] = useState([]);

    //useEffect(() => {
    //    const { data, error} = useAsync({promiseFn: fetchData})
    //    console.log(data);
    //    setPlotInput([data]);
    //}, []);

    const { data, error } = useAsync({ promiseFn: fetchData, setPlotInput })
    //const { data, error } = useFetch('./temporal_dev', {
    //    headers: { accept: "application/json" },
    //})

    //var idle_time = data['idle_time_pctg'];
    //var compute_time = data['compute_time_pctg'];
    //var non_compute_time = data['non_compute_time_pctg'];
    //var rank = data['rank'];
    //var input = [data];
    return (
        <>
            <Plot data= {plotInput} />
        </>
    );
};

export default TemporalView;
