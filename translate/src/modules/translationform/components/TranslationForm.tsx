import { Localized } from '@fluent/react';
import React, { useCallback, useContext, useLayoutEffect, useRef } from 'react';

import { EditorData, useEditorValue } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { usePluralExamples } from '~/hooks/usePluralExamples';
import { searchBoxHasFocus } from '~/modules/search/components/SearchBox';
import { CLDR_PLURALS } from '~/utils/constants';

import { EditAccesskey } from './EditAccesskey';
import { EditField, EditFieldProps } from './EditField';
import './TranslationForm.css';

const Label = ({
  getExample,
  htmlFor,
  labels,
}: {
  getExample: (label: string) => number | undefined;
  htmlFor: string;
  labels: Array<{ label: string; plural: boolean }>;
}) => (
  <label htmlFor={htmlFor}>
    {labels.map(({ label, plural }, index) => {
      const example = plural && getExample(label);
      const key = label + index;
      if (typeof example === 'number') {
        return (
          <Localized
            id='translationform--label-with-example'
            key={key}
            vars={{ example, label }}
            elems={{ stress: <span className='stress' /> }}
          >
            <span>
              {label} (e.g. <span className='stress'>{example}</span>)
            </span>
          </Localized>
        );
      } else {
        return <span key={key}>{label}</span>;
      }
    })}
  </label>
);

const EditPattern = (props: EditFieldProps & { name: string }) =>
  props.name.endsWith('accesskey') && props.value.length <= 1 ? (
    <EditAccesskey {...props} />
  ) : (
    <EditField {...props} />
  );

/**
 * Rich Editor for supported Fluent strings.
 *
 * This shows the Fluent translation based on its AST, presenting a nicer
 * interface to the user. The translation is stored as an AST, and changes
 * are made directly to that AST.
 */
export function TranslationForm(): React.ReactElement<'div'> {
  const { entity } = useContext(EntityView);
  const { fields, focusField, machinery } = useContext(EditorData);
  const value = useEditorValue();

  const userInput = useRef(false);

  const locale = useContext(Locale);
  const pluralExamples = usePluralExamples(locale);
  const getExample = useCallback(
    (label: string) => {
      const pluralForm = CLDR_PLURALS.indexOf(label);
      return pluralExamples && pluralForm >= 0
        ? pluralExamples[pluralForm]
        : undefined;
    },
    [pluralExamples],
  );

  // Reset the currently focused element when the entity changes or when
  // the translation changes from an external source.
  useLayoutEffect(() => {
    if (userInput.current) {
      userInput.current = false;
    } else {
      let input = fields[focusField.current]?.current;
      if (!input) {
        focusField.current = 0;
        input = fields[0]?.current;
      }
      if (input && !searchBoxHasFocus()) {
        input.focus();
        input.setSelectionRange(input.value.length, input.value.length);
      }
    }
  }, [entity, machinery, value]);

  const handleFocus = useCallback(
    (ev: { currentTarget: HTMLInputElement | HTMLTextAreaElement | null }) => {
      for (let i = 0; i < fields.length; ++i) {
        if (fields[i].current === ev.currentTarget) {
          focusField.current = i;
          return;
        }
      }
      focusField.current = -1;
    },
    [focusField, fields],
  );

  return value.length === 1 ? (
    <EditField
      inputRef={fields[0]}
      key={entity.pk}
      singleField
      userInput={userInput}
      value={value[0]?.value}
    />
  ) : (
    <div className='translationform' key={entity.pk}>
      <table>
        <tbody>
          {value.map(({ id, labels, name, value }, i) => (
            <tr key={id}>
              <td>
                <Label getExample={getExample} htmlFor={id} labels={labels} />
              </td>
              <td>
                <EditPattern
                  id={id}
                  inputRef={fields[i]}
                  name={name}
                  onFocus={handleFocus}
                  userInput={userInput}
                  value={value}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
