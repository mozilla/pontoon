
import {Loader} from 'loaders'

import TagResourcesButton from './button';


export default class TagResourcesLoader extends Loader {

    get selector () {
        return '.js-tag-resources';
    }

    get component () {
        return TagResourcesButton;
    }

    getProps (node) {
        return {
            api: node.dataset.api,
            tag: node.dataset.tag,
            project: node.dataset.project}
    }
}

document.addEventListener("DOMContentLoaded", () => new TagResourcesLoader().load())
