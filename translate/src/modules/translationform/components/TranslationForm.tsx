import { Localized } from '@fluent/react';
import React, {
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

import { EditFieldHandle, EditorData } from '../../../../src/context/Editor';
import { EntityView } from '../../../../src/context/EntityView';
import { Locale } from '../../../../src/context/Locale';
import { usePluralExamples } from '../../../../src/hooks/usePluralExamples';
import { searchBoxHasFocus } from '../../../../src/modules/search/components/SearchBox';
import { CLDR_PLURALS } from '../../../../src/utils/constants';

import { EditAccesskey } from './EditAccesskey';
import { EditField } from './EditField';
import './TranslationForm.css';

const Label = ({
  getExample,
  labels,
}: {
  getExample: (label: string) => number | undefined;
  labels: Array<{ label: string; plural: boolean }>;
}) => (
  <label>
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

/**
 * Rich Editor for supported Fluent strings.
 *
 * This shows the Fluent translation based on its AST, presenting a nicer
 * interface to the user. The translation is stored as an AST, and changes
 * are made directly to that AST.
 */
export function TranslationForm(): React.ReactElement<'div'> | null {
  const { entity } = useContext(EntityView);
  const { fields, focusField, machinery, pk, sourceView } =
    useContext(EditorData);
  const [shouldFocus, setShouldFocus] = useState(true);

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

  // Reset the currently focused element when the entity changes or
  // the translation changes from an external source.
  useEffect(() => {
    if (!searchBoxHasFocus()) {
      setShouldFocus(true);
    }
  }, [entity, machinery, fields]);

  const fieldValues = useMemo(
    () =>
      fields.map((field) => ({
        onFocus() {
          focusField.current = field;
        },
        ref(handle: EditFieldHandle | null) {
          if (handle) {
            field.handle.current = handle;
            if (shouldFocus && field.id === focusField.current?.id) {
              handle.focus();
              setShouldFocus(false);
            }
          }
        },
      })),
    [fields, focusField, shouldFocus],
  );

  return pk !== entity.pk ? null : fields.length === 1 ? (
    <div className='singlefield'>
      <EditField
        ref={fieldValues[0].ref}
        key={sourceView ? 's!' + pk : pk}
        defaultValue={fields[0].handle.current.value}
        index={0}
        singleField
      />
    </div>
  ) : (
    <div className='translationform' key={entity.pk}>
      <table>
        <tbody>
          {fields.map(({ handle, id, labels, name }, i) => {
            const value = handle.current.value;
            const EditPattern =
              name.endsWith('accesskey') && value.length <= 1
                ? EditAccesskey
                : EditField;
            const { onFocus, ref } = fieldValues[i];
            return (
              <tr key={id}>
                <td>
                  <Label getExample={getExample} labels={labels} />
                </td>
                <td>
                  <EditPattern
                    key={pk + id}
                    ref={ref}
                    defaultValue={value}
                    index={i}
                    name={name}
                    onFocus={onFocus}
                  />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
