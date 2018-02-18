
import React from 'react';

import WheelChart from 'widgets/charts/wheel';


export default class SummaryChart extends React.PureComponent {
    items = {
        fuzzy: 'rgb(254, 210, 113)',
        suggested: 'rgb(79, 196, 246)',
        translated: 'rgb(123, 200, 118)',
        missing: 'rgb(77, 89, 103)'};

    get chartData () {
        // zip stats with item colors
        return Object.assign(
            ...Object.entries(this.items).map(([k, v]) => (
                {[k]: {
                    value: this.props.stats[k].value,
                    color: v}})));
    }

    get percentageComplete () {
        return this.totalStrings ? parseInt(this.translatedStrings / this.totalStrings * 100) : 0;
    }

    get totalStrings () {
        return this.props.stats ? this.props.stats.all.value : 0;
    }

    get translatedStrings () {
        return this.props.stats ? this.props.stats.translated.value : 0;
    }

    render () {
        if (!this.props.stats) {
            return;
        }
        return (
            <WheelChart
               data={this.chartData}
               total={this.totalStrings}
               percentage={this.percentageComplete} />);
    }
}
