/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';
import onClickOutside from 'react-onclickoutside';

import './ProjectInfo.css';

import type { ProjectState } from 'core/project';

type Props = {|
    projectSlug: string,
    project: ProjectState,
|};

type State = {|
    visible: boolean,
|};

/**
 * Show a panel with the information provided for the current project.
 */
export class ProjectInfoBase extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            visible: false,
        };
    }

    toggleVisibility = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
    };

    // This method is called by the Higher-Order Component `onClickOutside`
    // when a user clicks outside the search panel.
    handleClickOutside = () => {
        this.setState({
            visible: false,
        });
    };

    render() {
        if (
            this.props.project.fetching ||
            !this.props.project.info ||
            this.props.projectSlug === 'all-projects'
        ) {
            return null;
        }

        return (
            <div className='project-info'>
                <div className='button' onClick={this.toggleVisibility}>
                    <span className='fa fa-info'></span>
                </div>
                {!this.state.visible ? null : (
                    <aside className='panel'>
                        <Localized id='projectinfo-ProjectInfo--project-info-title'>
                            <h2>Project Info</h2>
                        </Localized>
                        {/* We can safely use project.info because it is validated by
                    bleach before being saved into the database. */}
                        <p
                            dangerouslySetInnerHTML={{
                                __html: this.props.project.info,
                            }}
                        />
                    </aside>
                )}
            </div>
        );
    }
}

export default onClickOutside(ProjectInfoBase);
