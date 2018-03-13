
import React from 'react';

import {Title} from 'widgets/title';
import {Section} from 'widgets/section';

import DashboardSummary from './summary';

import './header.css';


export default class DashboardHeader extends React.PureComponent {

    get components () {
        const components = {
            title: Title,
            summary: DashboardSummary};
        return Object.assign({}, components, (this.props.components || {}));
    }

    render () {
        return (
            <Section id="heading">
              {this.renderTitle()}
              {this.renderSummary()}
            </Section>);
    }

    renderSummary () {
        const {components, ...props} = this.props;
        const Summary = this.components.summary;
        return <Summary {...props} />;
    }

    renderTitle () {
        const {components, ...props} = this.props;
        const Title = this.components.title;
        return (
            <Title
               {...props} />);
    }
}
