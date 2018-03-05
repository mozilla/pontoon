
import {Dashboard} from 'components/dashboard';
import {dataManager} from 'utils/data';
import TagLocalesDashboardDataManager from './manager';

const ProjectTagLocalesDashboard = dataManager(Dashboard, TagLocalesDashboardDataManager, window.DATA);

export default ProjectTagLocalesDashboard;
