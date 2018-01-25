
import React from 'react';
import ReactDOM from 'react-dom';

import TagResourceManager from './manager';


export class TagResourcesButton extends React.Component {

    constructor (props) {
        super(props);
        this.handleClick = this.handleClick.bind(this);
        this.state = {open: false};
    }

    handleClick (evt) {
        evt.preventDefault();
        const {open} = this.state;
        this.setState({open: !open});
    }

    renderButton () {
        const {open} = this.state;
        let message = "Manage resources for this tag";
        if (open) {
            message = "Hide the resource manager for this tag";
        }
        return (
              <button onClick={this.handleClick}>
                {message}
              </button>);
    }

    renderResourceManager () {
        const {open} = this.state;
        if (!open) {
            return '';
        }
        return (
            <TagResourceManager
               tag={this.props.tag}
               api={this.props.api}
               project={this.props.project} />);
    }

    render () {
        return (
            <div>
              {this.renderButton()}
              {this.renderResourceManager()}
            </div>);
    }
}


export class TagResourcesLoader {

    get tagResourceNodes () {
        return [...document.querySelectorAll('div.js-tag-resources')];
    }

    addButton (node) {
        ReactDOM.render(
            <TagResourcesButton
               api={node.dataset.api}
               tag={node.dataset.tag}
               project={node.dataset.project} />,
            node);
    }

    addButtons () {
        this.tagResourceNodes.forEach(this.addButton);
    }
}


document.addEventListener("DOMContentLoaded",function(){
    const loader = new TagResourcesLoader();
    loader.addButtons();
});
