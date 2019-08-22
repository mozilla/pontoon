/* @flow */

export type FluentMessage = {
    type: string,
    value: {
        elements: Array<{}>,
    },
    attributes: ?Array<{
        id: { name: string },
        value: {
            elements: Array<{}>,
        },
    }>,
    clone: () => FluentMessage,
    equals: (any) => boolean,
};
