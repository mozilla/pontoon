
import React from 'react';

import {List} from 'widgets/lists/generic';

import ProgressChartLegendItem from './legend-item';


export default class ProgressChartLegend extends React.PureComponent {

    get components () {
        const components = {item: ProgressChartLegendItem};
        return Object.assign({}, components, (this.props.components || {}));
    }

    render () {
        return (
            <List
               className="legend"
               items={Object.entries(this.props.items)}
               components={this.components} />);
    }
}
