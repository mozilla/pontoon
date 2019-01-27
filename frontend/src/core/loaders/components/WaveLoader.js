/* @flow */

import React from 'react';

import './WaveLoader.css';

type Props = {
    isLoading: boolean,
    children?: React.Node,
};

export class WaveLoadingBar extends React.Component {
    render() {
        return (<div id="project-load" className="overlay">
            <div className="inner">
                <div className="animation">
                    <div></div>
                    &nbsp;
                    <div></div>
                    &nbsp;
                    <div></div>
                    &nbsp;
                    <div></div>
                    &nbsp;
                    <div></div>
                </div>
                <div className="text">&quot;640K ought to be enough for anybody.&quot;</div>
            </div>
        </div>);
    }
}

// const WaveLoader = (props: Props): React.Node => React(
//     // Render children components, because some of fetches happen after components are rendered.
//      props.isLoading ? <WaveLoadingBar /> : props.children
// );
class WaveLoader extends React.Component<Props> {
    render() {
    const props = this.props;
    // Render children components, because some of fetches happen after components are rendered.
        return props.isLoading ? <WaveLoadingBar /> : props.children;
    }
}

export default WaveLoader;
