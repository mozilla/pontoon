
import ReactDOM from 'react-dom';
import React from 'react';

import {NotImplementedError} from 'errors';


export default class Loader {
    // finds nodes in the dom for `this.selector`, creates
    // components of type `this.component`, and then renders
    // the components into `this.getRenderNode(node)` for each
    // found node

    constructor () {
        this.load = this.load.bind(this);
        this.mountComponent = this.mountComponent.bind(this);
    }

    get nodes () {
        return [...document.querySelectorAll(this.selector)];
    }

    get component () {
        throw new NotImplementedError();
    }

    get selector () {
        throw new NotImplementedError();
    }

    getProps () {
        return {};
    }

    getRenderNode (node) {
        return node;
    }

    load () {
        this.nodes.forEach(this.mountComponent);
    }

    mountComponent (node) {
        const Component = this.component;
        const target = this.getRenderNode(node);
        // remove existing component gracefully
        this.unmountComponent(node);
        target.innerHTML = '';
        ReactDOM.render(
            <Component {...this.getProps(node)} />,
            target);
    }

    unmountComponent (node) {
        ReactDOM.unmountComponentAtNode(this.getRenderNode(node));
    }
}
