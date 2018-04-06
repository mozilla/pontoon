
import React from 'react';

import {List} from 'widgets/lists/generic';

import ProgressChartLegendItem from './legend-item';


export default class ProgressChartLegend extends React.PureComponent {
    components = {item: ProgressChartLegendItem};

    render () {
        const {item: Item = this.components.item} = (this.props.components || {});
        return (
            <List
               className="legend"
               items={Object.entries(this.props.items)}
               components={{item: Item}} />);
    }
}
