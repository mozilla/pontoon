/* @flow */

export type FluentElement = {
    type: string,
    value: string,
};

export type FluentValue = {
    elements: Array<FluentElement>,
};

export type FluentAttribute = {
    id: { name: string },
    value: FluentValue,
};

export type FluentAttributes = Array<FluentAttribute>;

export type FluentMessage = {
    type: string,
    value: FluentValue,
    attributes: ?FluentAttributes,
    clone: () => FluentMessage,
    equals: (any) => boolean,
};
