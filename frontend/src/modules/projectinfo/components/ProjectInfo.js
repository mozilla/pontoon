/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';

import './ProjectInfo.css';

import * as navigation from 'core/navigation';
import * as project from 'core/project';

import InfoPanel from './InfoPanel';

import type { NavigationParams } from 'core/navigation';
import type { ProjectState } from 'core/project';


type Props = {|
    parameters: NavigationParams,
    project: ProjectState,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};


/**
 * Render the current project's completion status and its info panel.
 */
export class ProjectInfoBase extends React.Component<InternalProps> {
    render() {
        if (
            this.props.project.fetching ||
            !this.props.project.name ||
            this.props.parameters.project === 'all-projects'
        ) {
            return null;
        }

        return <div className="project-info">
            <InfoPanel info={ this.props.project.info } />
        </div>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        parameters: navigation.selectors.getNavigationParams(state),
        project: state[project.NAME],
    };
};

export default connect(mapStateToProps)(ProjectInfoBase);
