// @ts-nocheck
import "./IdleTimeView.css"
import { useFetch, useAsync } from "react-async"
import { useState, useEffect } from 'react'
import { Button, Dropdown, message, Space, Tooltip, Layout, Typography } from 'antd';
import { DownOutlined } from '@ant-design/icons';
import Plot from 'react-plotly.js';

const handleButtonClick = (e) => {
  message.info('Click on left button.');
  console.log('click left button', e);
};

const fetchData = async ( {setPlotInput, rank} ) => {
    const response = await fetch(`./idle_time?` + new URLSearchParams({rank}), {
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

const fetchNumRanks = async ( {setNumRanks} ) => {
    const response = await fetch(`./num_ranks`, {
        headers: { accept: "application/json" },
    })
    var out = await response.json();
    var num_ranks = parseInt(out['num_ranks']);
    
    console.log('inside');
    console.log(response);
    console.log(num_ranks);
    setNumRanks(num_ranks);

    return response;
}

function TemporalView() {
    const [plotInput, setPlotInput] = useState({});
    const [rank, setRank] = useState(0);
    const [numRanks, setNumRanks] = useState(0);
    const [visualizePct, setVisualizePct] = useState(true);

    useEffect(() => {
        //var {data, error} = useAsync({ promiseFn: fetchData, setPlotInput, rank })
        const fetchData = async ( {setPlotInput, rank, visualizePct} ) => {
            const response = await fetch(`./idle_time?` + new URLSearchParams({rank, visualizePct}), {
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
        fetchData({ setPlotInput, rank, visualizePct });
    }, [setPlotInput, rank, visualizePct]);

    //const { data, error } = useAsync({ promiseFn: fetchData, setPlotInput, rank })
    const { output, error2 } = useAsync({ promiseFn: fetchNumRanks, setNumRanks })

    const handleRankChange = async (e) => {
        let i = parseInt(e['key']);
        setRank(i);
        message.info('Click on menu item.');
        console.log('click', e);
    };
    const rankItems = [];
    const rankMenuProps = {
        items: rankItems,
        onClick: handleRankChange,
    };
    for (let i = 0; i < numRanks; i++) {
        let item = {
            label: `Rank ${i}`,
            key: i,
        };
        rankItems.push(item);
    }
    console.log(rankItems);

    const handlePctChange = async (e) => {
        var i = (e['key'] === 'true');
        console.log(i);
        setVisualizePct(i);
        message.info('Click on menu item.');
        console.log('click', e);
    };
    const tfItems = [
        {
            label: 'True',
            key: true,
        },
        {
            label: 'False',
            key: false,
        },
    ];
    const tfMenuProps = {
        items: tfItems,
        onClick: handlePctChange,
    };
    
    return (
        <>
            <Layout>
                <Layout.Content className="innercontent">
                    <Plot data= {plotInput.data} layout= {plotInput.layout} />
                </Layout.Content>
                <Layout.Sider theme="light">  
                    <Typography.Title level={3} style={{ textAlign: "center" }}>
                        View Options
                    </Typography.Title>
                    <Dropdown menu={rankMenuProps}>
                      <Button  block={true}>
                        <Space>
                          Rank {rank}
                          <DownOutlined />
                        </Space>
                      </Button>
                    </Dropdown>
                    <Dropdown menu={tfMenuProps}>
                      <Button  block={true}>
                        <Space>
                          View Percent: {visualizePct.toString()}
                          <DownOutlined />
                        </Space>
                      </Button>
                    </Dropdown>
                </Layout.Sider>
            </Layout>
        </>
    );
}

export default TemporalView
