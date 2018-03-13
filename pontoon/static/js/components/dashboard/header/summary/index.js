
import React from 'react';

import {Columns} from 'widgets/columns';
import {InfoList} from 'widgets/lists/info';
import SummaryChart from './chart';
import {SummaryStats} from './stats';


export default class DashboardSummary extends React.PureComponent {

    get components () {
        const components = {
            info: InfoList,
            chart: SummaryChart,
            stats: SummaryStats};
        return Object.assign({}, components, (this.props.components || {}));
    }

    get columns () {
        const {
            info: SummaryInfo,
            chart: SummaryChart,
            stats: SummaryStats} = this.components;
        const {components, ...props} = this.props;
        return [
            [<SummaryInfo {...props} />, 3],
            [<SummaryChart {...props}  />, 2],
            [<SummaryStats {...props} />, 3]];
    }

    render () {
        return <Columns columns={this.columns} />;
    }
}
