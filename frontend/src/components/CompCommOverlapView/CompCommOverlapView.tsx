// @ts-nocheck
import "./CompCommOverlapView.css"
import { useFetch, useAsync } from "react-async"
import { useState, useEffect } from 'react'
import { Layout } from 'antd';
import Plot from 'react-plotly.js';

function CompCommOverlapView() {
    const [plotInput, setPlotInput] = useState({});

    useEffect(() => {
        //var {data, error} = useAsync({ promiseFn: fetchData, setPlotInput, rank })
        const fetchData = async ({ setPlotInput }) => {
            const response = await fetch(`./comp_comm_overlap`, {
                headers: { accept: "application/json" },
            })

            if (!response.ok) throw new Error(response.status)
            var out = await response.json();
            setPlotInput(out);
            //console.log('inside');
            //console.log(response);
            //console.log(out);
            //console.log(out['idle_time_pctg']);
            return response;
        }

        //var {data, error} = useAsync({ promiseFn: fetchData, setPlotInput, rank })
        fetchData({ setPlotInput });
    }, [setPlotInput]);

    return (
        <>
            <Layout>
                <Layout.Content className="innercontent">
                    <Plot data={plotInput.data} layout={plotInput.layout} />
                </Layout.Content>
            </Layout>
        </>
    );
}

export default CompCommOverlapView;
