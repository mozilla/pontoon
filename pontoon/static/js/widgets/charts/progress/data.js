
import React from 'react';

import ProgressChartDataItem from './data-item';


export default class ProgressChartData extends React.PureComponent {

    get className () {
        return this.props.className || "chart";
    }

    get components () {
        const components = {item: ProgressChartDataItem};
        return Object.assign({}, components, (this.props.components || {}));
    }

    render () {
        return (
            <div className="chart-wrapper">
              {this.renderTotal()}
              {this.renderChart()}
            </div>);
    }

    renderTotal () {
        return (
            <span className="percent">
              {this.props.data.total}%
            </span>);
    }

    renderChart () {
        const {item: Item} = this.components;
        const {total, ...items} = this.props.data;
        return (
            <span className={this.className}>
                {Object.entries(items).map(([name, data], key) => {
                    return (
                        <Item
                           className={name}
                           data={data}
                           key={key} />);
                })}
            </span>);
    }
}
