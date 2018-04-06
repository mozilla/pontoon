
import React from 'react';

import ProgressChartData from './data';
import ProgressChartLegend from './legend';

import './progress.css';


export default class ProgressChart extends React.PureComponent {
    components = {data: ProgressChartData, legend: ProgressChartLegend};

    render () {
        const {components, stats, percentages} = this.props;
        const {
            data: Data = this.components.data,
            legend: Legend = this.components.legend} = (components || {});
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
