
import React from 'react';

import {InfoList} from 'widgets/lists/info';
import {Stars} from 'widgets/stars';
import {Deadline} from 'widgets/deadline';


export default class ProjectSummaryInfo extends React.PureComponent {

    get data () {
        return this.props.data ? this.props.data.dashboard.context : undefined;
    }

    get repoURL () {
        return this.data.repository.replace(/(^\w+:|^)\/\//, '');
    }

    get summaryInfo () {
        const info = {};
        const defaults = {
            'Priority': this.renderPriority(),
            'Deadline': this.renderDeadline(),
            'Repository': this.renderRepository(),
            'Contact Person': this.renderUser()};
        const mapping = this.props.items || defaults;
        Object.entries(mapping).forEach(([k, v]) => {
            if (v) {
                info[k] = v;
            } else if (k in defaults) {
                info[k] = defaults[k];
            }
        });
        return info;
    }

    render () {
        if (!this.data) {
            return '';
        }
        const {data, ...props} = this.props;
        return (
            <InfoList
               {...props}
               items={this.summaryInfo}  />);
    }

    renderDeadline () {
        return <Deadline deadline={this.data.deadline} />;
    }

    renderRepository () {
        return (
            <a className="overflow" href={this.data.repository}>{this.repoURL}</a>
        );
    }

    renderPriority () {
        return <Stars stars={this.data.priority} total={5} />;
    }

    renderUser () {
        return (
            <span><a href={this.data.user.url}>{this.data.user.name}</a></span>
        );
    }
}
