// @ts-nocheck
import "./IdleTimeView.css"
import { useFetch, useAsync } from "react-async"
import { useState, useEffect } from 'react'
import { Button, Dropdown, message, Space, Tooltip, Layout } from 'antd';
import { DownOutlined } from '@ant-design/icons';
import Plot from 'react-plotly.js';

const handleButtonClick = (e) => {
  message.info('Click on left button.');
  console.log('click left button', e);
};
const handleMenuClick = (e) => {
  message.info('Click on menu item.');
  console.log('click', e);
};
const items = [
  {
    label: '1st menu item',
    key: '1',
  },
  {
    label: '2nd menu item',
    key: '2',
  },
  {
    label: '3rd menu item',
    key: '3',
  },
  {
    label: '4rd menu item',
    key: '4',
  },
];
const menuProps = {
  items,
  onClick: handleMenuClick,
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
    
    console.log('inside');
    console.log(response);
    console.log(out);
    //setNumRanks(out);
    return response;
}

const TemporalView = ({ menu }) => {
    const [plotInput, setPlotInput] = useState({});
    const [rank, setRank] = useState(0);
    const [numRanks, setNumRanks] = useState(0);

    const { data, error } = useAsync({ promiseFn: fetchData, setPlotInput, rank })
    const { output, error2 } = useAsync({ promiseFn: fetchNumRanks, setNumRanks })
    return (
        <>
            <Layout>
                <Layout.Content className="innercontent">
                    <Plot data= {plotInput.data} layout= {plotInput.layout} />
                </Layout.Content>
                <Layout.Sider> Sider Test 
                    <Dropdown menu={menuProps}>
                      <Button>
                        <Space>
                          Button
                          <DownOutlined />
                        </Space>
                      </Button>
                    </Dropdown>
                </Layout.Sider>
            </Layout>
        </>
    );
};

export default TemporalView;
