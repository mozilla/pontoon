import * as React from 'react';
import { Localized } from '@fluent/react';

import { useOnDiscard } from 'core/utils';

import './ProjectInfo.css';

import type { ProjectState } from 'core/project';

type Props = {
    projectSlug: string;
    project: ProjectState;
};

type State = {
    visible: boolean;
};

type ProjectInfoProps = {
    project: ProjectState;
    onDiscard: () => void;
};

export function ProjectInfo({
    project,
    onDiscard,
}: ProjectInfoProps): React.ReactElement<'aside'> {
    const ref = React.useRef(null);
    useOnDiscard(ref, onDiscard);
    return (
        <aside ref={ref} className='panel'>
            <Localized id='projectinfo-ProjectInfo--project-info-title'>
                <h2>PROJECT INFO</h2>
            </Localized>
            {/* We can safely use project.info because it is validated by
                bleach before being saved into the database. */}
            <p
                dangerouslySetInnerHTML={{
                    __html: project.info,
                }}
            />
        </aside>
    );
}

/**
 * Show a panel with the information provided for the current project.
 */
export default class ProjectInfoBase extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            visible: false,
        };
    }

    toggleVisibility: () => void = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
    };

    handleDiscard: () => void = () => {
        this.setState({
            visible: false,
        });
    };

    render(): null | React.ReactElement<'div'> {
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
                {this.state.visible && (
                    <ProjectInfo
                        project={this.props.project}
                        onDiscard={this.handleDiscard}
                    />
                )}
            </div>
        );
    }
}
