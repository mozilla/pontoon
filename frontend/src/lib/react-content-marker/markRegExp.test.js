import React from 'react';

import markRegExp from './markRegExp';


describe('markRegExp', () => {
    it('correctly marks matches of a simple pattern', () => {
        const content = 'A horse, a horse, my kingdom for a horse.';

        const res = markRegExp(content, /(horse)/, x => <mark>{x}</mark>);
        const expected = [
            'A ',
            <mark>{ 'horse' }</mark>,
            ', a ',
            <mark>{ 'horse' }</mark>,
            ', my kingdom for a ',
            <mark>{ 'horse' }</mark>,
            '.',
        ];
        expect(res).toEqual(expected);
    });

    it('correctly marks matches of a more complex pattern', () => {
        const content = 'Foux du fa fa';

        const res = markRegExp(content, /(f\w+)/i, x => <mark>{x}</mark>);
        const expected = [
            <mark>{ 'Foux' }</mark>,
            ' du ',
            <mark>{ 'fa' }</mark>,
            ' ',
            <mark>{ 'fa' }</mark>,
        ];
        expect(res).toEqual(expected);
    });

    it('correctly marks the entire content', () => {
        const content = 'horse';

        const res = markRegExp(content, /(horse)/, x => <mark>{x}</mark>);
        const expected = [
            <mark>{ 'horse' }</mark>,
        ];
        expect(res).toEqual(expected);
    });

    it('supports attributes in tag', () => {
        const content = 'word';

        const res = markRegExp(
            content, /(word)/, x => <mark title='Word Finder'>{x}</mark>
        );

        const expected = [
            <mark title='Word Finder'>{ 'word' }</mark>,
        ];
        expect(res).toEqual(expected);
    });

    it('returns the input as an array if there is no match', () => {
        const content = 'A horse, a horse, my kingdom for a horse.';

        const res = markRegExp(content, /(missing)/, x => <mark>{x}</mark>);

        const expected = [content];
        expect(res).toEqual(expected);
    });

    it('supports having several capturing groups in the rule', () => {
        const content = 'A horse, a horse, my kingdom for a horse.';

        const res = markRegExp(content, /(a (horse)|A (horse))/, x => <mark>{x}</mark>);

        const expected = [
            'A ',
            <mark>{ 'horse' }</mark>,
            ', a ',
            <mark>{ 'horse' }</mark>,
            ', my kingdom for a ',
            <mark>{ 'horse' }</mark>,
            '.',
        ];
        expect(res).toEqual(expected);
    });
});
