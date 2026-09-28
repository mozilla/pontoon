import type { Message } from '@mozilla/l10n';
import React, { createContext, useContext, useState, useRef } from 'react';
import {
  type ComposedMachineryTranslation,
  type MachineryTranslation,
  fetchOpenAIComposedTranslation,
  fetchOpenAITranslation,
} from '~/api/machinery';

type ComposedRefinement = {
  value: Message;
  properties?: Record<string, Message>;
};

type SelState = {
  loading: boolean;
  selectedOption: string;
  llmTranslation: string;
  llmComposed: ComposedRefinement | null;
};

/** Object identity keys either kind in the WeakMap. */
type Refinable = MachineryTranslation | ComposedMachineryTranslation;

interface LLMTranslationContextType {
  getSelState(mt: Refinable): SelState;
  transformLLMTranslation: (
    mt: MachineryTranslation,
    characteristic: string,
    localeCode: string,
    entityPk?: number,
  ) => Promise<void>;
  transformComposedLLMTranslation: (
    ct: ComposedMachineryTranslation,
    characteristic: string,
    localeCode: string,
    entityPk: number,
  ) => Promise<void>;
  restoreOriginal: (mt: Refinable) => void;
}

const initSelState = () => ({
  loading: false,
  selectedOption: '',
  llmTranslation: '',
  llmComposed: null,
});

const LLMTranslationContext = createContext<LLMTranslationContextType>({
  getSelState: initSelState,
  transformLLMTranslation: async () => {},
  transformComposedLLMTranslation: async () => {},
  restoreOriginal: () => {},
});

export const LLMTranslationProvider: React.FC = ({ children }) => {
  const stateRef = useRef(new WeakMap<Refinable, SelState>());
  const [, setVersion] = useState(0); // Counter to trigger re-renders

  const getSelState = (mt: Refinable): SelState => {
    return stateRef.current.get(mt) ?? initSelState();
  };

  const setLoading = (mt: Refinable) => {
    stateRef.current.set(mt, { ...getSelState(mt), loading: true });
    setVersion((v) => v + 1); // Trigger re-render
  };

  const transformLLMTranslation = async (
    mt: MachineryTranslation,
    characteristic: string,
    localeCode: string,
    entityPk?: number,
  ) => {
    const currentState = getSelState(mt);
    setLoading(mt);

    const machineryTranslations = await fetchOpenAITranslation(
      mt.original,
      { [mt.sources[0]]: [mt.translation] },
      characteristic,
      localeCode,
      entityPk,
    );
    if (machineryTranslations.length > 0) {
      stateRef.current.set(mt, {
        loading: false,
        selectedOption: characteristic,
        llmTranslation: machineryTranslations[0].translation,
        llmComposed: null,
      });
    } else {
      stateRef.current.set(mt, {
        ...currentState,
        loading: false,
      });
    }
    setVersion((v) => v + 1);
  };

  const transformComposedLLMTranslation = async (
    ct: ComposedMachineryTranslation,
    characteristic: string,
    localeCode: string,
    entityPk: number,
  ) => {
    const currentState = getSelState(ct);
    setLoading(ct);

    const refined = await fetchOpenAIComposedTranslation(
      entityPk,
      ct.value,
      ct.properties,
      characteristic,
      localeCode,
    );
    if (refined) {
      stateRef.current.set(ct, {
        loading: false,
        selectedOption: characteristic,
        llmTranslation: '',
        llmComposed: refined,
      });
    } else {
      stateRef.current.set(ct, {
        ...currentState,
        loading: false,
      });
    }
    setVersion((v) => v + 1);
  };

  const restoreOriginal = (mt: Refinable) => {
    const currentState = getSelState(mt);
    stateRef.current.set(mt, {
      ...currentState,
      selectedOption: '',
      llmTranslation: '',
      llmComposed: null,
    });
    setVersion((v) => v + 1);
  };
  return (
    <LLMTranslationContext.Provider
      value={{
        getSelState,
        transformLLMTranslation,
        transformComposedLLMTranslation,
        restoreOriginal,
      }}
    >
      {children}
    </LLMTranslationContext.Provider>
  );
};

export const useLLMTranslation = () => {
  const {
    getSelState,
    transformLLMTranslation,
    transformComposedLLMTranslation,
    restoreOriginal,
  } = useContext(LLMTranslationContext);

  return (mt: Refinable) => ({
    ...getSelState(mt),
    transformLLMTranslation,
    transformComposedLLMTranslation,
    restoreOriginal,
  });
};
