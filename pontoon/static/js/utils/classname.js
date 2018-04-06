
export const getClass = (component) => {
    const classes = [];
    const {className, props} = component;
    if (className) {
        classes.push(className)
    }
    if (props.className) {
        classes.push(className)
    }
    return classes.join(' ');
}
