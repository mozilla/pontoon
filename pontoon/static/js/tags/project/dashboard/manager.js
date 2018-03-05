
import {DashboardBody} from 'components/dashboard';

import {componentManager} from 'utils/components';

import ProjectTagsStatsTable from './table';
import {ProjectDashboardManager} from 'projects/dashboard';


export default class ProjectTagsDashboardManager extends ProjectDashboardManager {

    get components () {
        const components = super.components;
        components.body = componentManager(
            DashboardBody,
            {content: ProjectTagsStatsTable});
        return components;
    }

    get statData () {
        let {data} = (this.component.state || {});
        return data ? data.dashboard.context.stats || {} : {};
    }
}
