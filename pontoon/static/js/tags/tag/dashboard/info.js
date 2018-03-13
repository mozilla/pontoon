
import React from 'react';

import {Stars} from 'widgets/stars';
import {ProjectSummaryInfo} from 'projects/dashboard';


export default class ProjectTagSummaryInfo extends React.PureComponent {

    get data () {
        return this.props.data ? this.props.data.dashboard.context : undefined;
    }

    get summaryInfo () {
        const info = {
            'Priority': null,
            'Tag priority': this.renderTagPriority(),
            'Deadline': null,
            'Repository': null,
            'Contact Person': null}
        return Object.assign({}, info, (this.props.info || {}));
    }

    render () {
        if (!this.data) {
            return '';
        }
        return <ProjectSummaryInfo {...this.props} items={this.summaryInfo} />
    }

    renderTagPriority () {
        return <Stars stars={this.props.data.tag.priority} total={5} />;
    }
}
