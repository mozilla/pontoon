
import {DashboardDataManager, DashboardHeader} from 'components/dashboard';
import DashboardSummary from 'components/dashboard/header/summary';
import {componentManager} from 'utils/components';

import ProjectSummaryInfo from './info';


export default class ProjectDashboardManager extends DashboardDataManager {

    get components () {
        const components = super.components;
        components.header = componentManager(
            DashboardHeader,
            {summary: componentManager(
                DashboardSummary,
                {info: ProjectSummaryInfo})});
        return components;
    }
}
