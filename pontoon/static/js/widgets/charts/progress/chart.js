
import React from 'react';

import ProgressChartData from './data';
import ProgressChartLegend from './legend';

import './progress.css';


export default class ProgressChart extends React.PureComponent {

    get components () {
        const components = {data: ProgressChartData, legend: ProgressChartLegend};
        return Object.assign({}, components, (this.props.components || {}));
    }

    render () {
        const {data: Data, legend: Legend} = this.components;
        const {stats, percentages} = this.props;
        return (
            <div className="progress-inline">
              <Data
                 data={percentages}
                 />
              <Legend
                 items={stats}
                 />
            </div>);
    }
}
