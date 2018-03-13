
import {Dashboard} from 'components/dashboard';
import {dataManager} from 'utils/data';
import ProjectTagsDashboardManager from './manager';

const ProjectTagsDashboard = dataManager(Dashboard, ProjectTagsDashboardManager, window.DATA);
export default ProjectTagsDashboard;
