import React from 'react';

import mark from './mark';
import markRegExp from './markRegExp';
import markTerm from './markTerm';


describe('mark', () => {
    it('works correctly with a `term` rule', () => {
        const content = 'A horse, a horse, my kingdom for a horse.';
        const rule = 'horse';
        const tag = x => <mark>{x}</mark>;

        const res = mark(content, rule, tag);
        const expected = markTerm(content, rule, tag);

        expect(res).toEqual(expected);
    });

    it('works correctly with a `regex` rule', () => {
        const content = 'A horse, a horse, my kingdom for a horse.';
        const rule = /(horse)/;
        const tag = x => <mark>{x}</mark>;

        const res = mark(content, rule, tag);
        const expected = markRegExp(content, rule, tag);

        expect(res).toEqual(expected);
    });

    it('works with an array input', () => {
        const content = [
            'Hello, ',
            <div />,
            'What is your name?',
        ];
        const rule = 'name';
        const tag = x => <mark>{x}</mark>;

        const res = mark(content, rule, tag);
        const expected = [
            'Hello, ',
            <div />,
            'What is your ',
            <mark>{ 'name' }</mark>,
            '?',
        ];

        expect(res).toEqual(expected);
    });

    it('can chain marks', () => {
        const content = 'My name is what my name is who my name is Slim Shady';
        const tag = x => <mark>{x}</mark>;

        let res = mark(content, 'name', tag);
        res = mark(res, /(wh\w+)/, tag);
        res = mark(res, /([A-Z]\w+ [A-Z]\w+)/, tag);

        const expected = [
            "My ",
            <mark>name</mark>,
            " is ",
            <mark>what</mark>,
            " my ",
            <mark>name</mark>,
            " is ",
            <mark>who</mark>,
            " my ",
            <mark>name</mark>,
            " is ",
            <mark>Slim Shady</mark>,
        ];

        expect(res).toEqual(expected);
    });
});
