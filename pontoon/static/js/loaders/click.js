
import Loader from './loader'


export default class ClickLoader extends Loader {
    // instead of loading components at the nodes identified by
    // `this.selector`, this Loader listens for clicks (or other events)
    // on them and loads the components when they happen

    // When this loader first loads it will check if any of the selected
    // nodes are "active" and simulate the trigger event if it is.

    constructor () {
        super();
        this.handle = this.handle.bind(this);
    }

    get event () {
        return "click";
    }

    isActive () {
        return false;
    }

    handle (evt) {
        if (this.nodes.indexOf(evt.target) !== -1) {
            evt.preventDefault();
            this.mountComponent(evt.target);
        }
    }

    load () {
        document.addEventListener(this.event, this.handle);
        this.nodes.forEach(node => {
            if (this.isActive(node)) {
                this.loadActive(node);
            }
        })
    }

    loadActive (node) {
        // give it a click on first load if its active
        node.click()
    }
}
