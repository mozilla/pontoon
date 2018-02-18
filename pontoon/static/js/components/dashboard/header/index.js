
import React from 'react';

import {Title} from 'widgets/title';
import {Section} from 'widgets/section';
import {getComponent} from 'utils/components';

import DashboardSummary from './summary';
import './header.css';


export default class DashboardHeader extends React.PureComponent {
    components = {
        title: Title,
        summary: DashboardSummary};

    render () {
        const {components, ...props} = this.props;
        return (
            <Section id="heading">
              {this.renderTitle(props)}
              {this.renderSummary(props)}
            </Section>);
    }

    renderSummary (props) {
        const Summary = getComponent(this, 'summary');
        return <Summary {...props} />;
    }

    renderTitle (props) {
        const Title = getComponent(this, 'title');
        return <Title {...props} />;
    }
}
