
import React from 'react';

import {Section} from 'widgets/section';


export default class DashboardBody extends React.PureComponent {

    get id () {
        return 'main';
    }

    render () {
        const {components, ...props} = this.props;
        const {content: Content} = (components || {});
        if (!Content) {
            return '';
        }
        return (
            <Section id={this.id}>
              <Content {...props} />
            </Section>);
    }
}
