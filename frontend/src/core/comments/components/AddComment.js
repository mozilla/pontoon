/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';
import { MentionsInput, Mention } from 'react-mentions';

import './AddComment.css';

import { UserAvatar } from 'core/user'

type Props = {|
    user: string,
    username: string,
    imageURL: string,
    translation?: ?number,
    projectManager?: string,
    addComment: (string, ?number) => void,
|};


export default function AddComments(props: Props) {
    const {
        user,
        username,
        imageURL,
        translation,
        addComment,
        projectManager,
    } = props;


    const commentInput: any = React.useRef();
    const [value, setValue] = React.useState('');

    if (!user) {
        return null;
    }

    const handleOnChange = () => {
        setValue(commentInput.current.value)
    }

    const handleOnKeyDown = (event: SyntheticKeyboardEvent<>) => {
        if (event.keyCode === 13 && event.shiftKey === false) {
            event.preventDefault();
            submitComment(event);
        }
    }

    const handleOnKeyDown = (event: SyntheticKeyboardEvent<>) => {
        if (event.keyCode === 13 && event.shiftKey === false) {
            submitComment(event);
        }
    }

    const submitComment = (event: SyntheticEvent<>) => {
        event.preventDefault();
        let comment = commentInput.current.value;

        if (!comment) {
            return null;
        }

        if (projectManager) {
            comment = `${projectManager}: ${comment}`;
        }

        addComment(comment, translation);

        setValue('');
    };

    return <div className='comment add-comment'>
        <UserAvatar
            username={ username }
            imageUrl={ imageURL }
        />
        <form className='container'>
            <Localized
                id='comments-AddComment--input'
                attrs={{ placeholder: true }}
            >
                <MentionsInput
                    className='text-area'
                    autoFocus
                    value={ value }
                    dir='auto'
                    placeholder={ `Write a comment…` }
                    inputRef={ commentInput }
                    onChange={ handleOnChange }
                    onKeyDown={ handleOnKeyDown }
                >
                    <Mention
                        trigger="@"
                        data={[{ id: 'abowler', display: 'April Bowler'}]}
                        markup="@[__display__](__type__:__id__)"
                        // renderSuggestion={(
                        //     suggestion,
                        //     search,
                        //     highlightedDisplay,
                        //     index,
                        //     focused
                        //   ) => (
                        //     <div className={`user ${focused ? 'focused' : ''}`}>
                        //       {highlightedDisplay}
                        //     </div>
                        //   )}
                    />
                </MentionsInput>
            </Localized>
            <Localized
                id="comments-AddComment--submit-button"
                attrs={{ title: true }}
                glyph={
                    <i className="fa fa-paper-plane"></i>
                }
            >
                <button
                    className="submit-button"
                    title="Submit comment"
                    onClick={ submitComment }
                >
                    { '<glyph></glyph>' }
                </button>
            </Localized>
        </form>
    </div>
}
