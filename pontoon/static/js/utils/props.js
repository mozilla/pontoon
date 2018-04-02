
export function appendProps(target, name, descriptor) {
  const {get} = descriptor;
  return {
    get: function () {
        const result = [get()];
        if (this.props[name]) {
            result.push(this.props[name]);
        }
        return result.join(' ');
    }
  };
}
