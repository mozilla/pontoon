
import React from 'react';

import {Columns} from 'widgets/columns';
import {InfoList} from 'widgets/lists/info';
import {getComponents} from 'utils/components';

import {SummaryStats} from './stats';
import SummaryChart from './chart';


export default class DashboardSummary extends React.PureComponent {
    components = {
        info: InfoList,
        chart: SummaryChart,
        stats: SummaryStats};

    get columns () {
        const {components, ...props} = this.props;
        const {
            info: SummaryInfo,
            chart: SummaryChart,
            stats: SummaryStats} = getComponents(this);
        return [
            [<SummaryInfo {...props} />, 3],
            [<SummaryChart {...props}  />, 2],
            [<SummaryStats {...props} />, 3]];
    }

    render () {
        return <Columns columns={this.columns} />;
    }
}
