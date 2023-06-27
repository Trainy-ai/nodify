// @ts-nocheck

import { useState } from 'react'
import { Layout } from "antd";
import TopicMenu from "./components/TopicMenu.jsx";
import SideBar from "./components/SideBar/SideBar.jsx";
import ProgressView from "./components/ProgressView/ProgressView.jsx"
import ConsistencyView from './components/ConsistencyView/ConsistencyView.js';
import UtilView from './components/UtilView/UtilView.js';
import './App.css'


function App() {
  const topics = ["Temporal", "Kernels", "Progress", "Consistency", "GPU Util"];
  const [contentIndex, setContentIndex] = useState(0);
  const [selectedKey, setSelectedKey] = useState("0");
  const changeSelectedKey = (event) => {
    const key = event.key;
    setSelectedKey(key);
    setContentIndex(+key);
  };
  const Menu = (
    <TopicMenu
      topics={topics}
      selectedKey={selectedKey}
      changeSelectedKey={changeSelectedKey}
    />
  );
  let plot;
  if (contentIndex == 0) {
    plot = <iframe src='./temporal.html'></iframe>;
  } else if (contentIndex == 1) {
    plot = <iframe src='./kernel.html'></iframe>;
  } else if (contentIndex == 2) {
    plot = <ProgressView />
  } else if (contentIndex == 3) {
    plot = <ConsistencyView />
  } else {
    plot = <UtilView />
  }
  return (
    <div className="App">
      <Layout>
        <SideBar menu={Menu} />
        <Layout.Content className="content">
          {plot}
        </Layout.Content>
      </Layout>
    </div>
  );
}

export default App
