export class NotImplementedError extends Error {
    constructor(...args) {
        super(...args);
        Error.captureStackTrace(this, NotImplementedError);
    }
}

NotImplementedError.prototype = Error.prototype;
