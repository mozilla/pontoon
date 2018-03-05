
import {DashboardBody, DashboardDataManager, DashboardHeader} from 'components/dashboard';
import DashboardSummary from 'components/dashboard/header/summary';
import {componentManager} from 'utils/components';

import TagLocaleStats from './stats';
import {TagLocalesStatsTable} from './table';
import ProjectTagSummaryInfo from './info';


export default class TagLocalesDashboardDataManager extends DashboardDataManager {

    get statsClass () {
        return TagLocaleStats;
    }

    get statData () {
        let {data} = (this.component.state || {});
        return data ? data.tag.data.map(x => Object.assign({}, x.chart, {name: x.name})) || {} : {};
    }

    get components () {
        const components = super.components;
        components.header = componentManager(
            DashboardHeader,
            {summary: componentManager(
                DashboardSummary,
                {info: ProjectTagSummaryInfo})});
        components.body = componentManager(
            DashboardBody,
            {content: TagLocalesStatsTable});
        return components;
    }

    get tabs () {
        const tabs = super.tabs;
        tabs[0].count = this.stats.data.length;
        return tabs;
    }
}
