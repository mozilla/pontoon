import React, { createContext, useContext, useState, useRef } from 'react';
import { type MachineryTranslation, fetchGPTTransform } from '~/api/machinery';

export type SelState = {
  loading: boolean;
  selectedOption: string;
  llmTranslations: Record<string, string>;
};

interface LLMTranslationContextType {
  getSelState(mt: MachineryTranslation): SelState;
  transformLLMTranslation: (
    mt: MachineryTranslation,
    characteristic: string,
    localeName: string,
  ) => Promise<void>;
  restoreOriginal: (mt: MachineryTranslation) => void;
}

const initSelState = () => ({
  loading: false,
  selectedOption: '',
  llmTranslations: {},
});

const LLMTranslationContext = createContext<LLMTranslationContextType>({
  getSelState: initSelState,
  transformLLMTranslation: async () => {},
  restoreOriginal: () => {},
});

export const LLMTranslationProvider: React.FC = ({ children }) => {
  const stateRef = useRef(new WeakMap<MachineryTranslation, SelState>());
  const [, setVersion] = useState(0); // Counter to trigger re-renders

  const getSelState = (mt: MachineryTranslation): SelState => {
    return stateRef.current.get(mt) ?? initSelState();
  };

  const transformLLMTranslation = async (
    mt: MachineryTranslation,
    characteristic: string,
    localeName: string,
  ) => {
    const currentState = getSelState(mt);
    stateRef.current.set(mt, {
      ...currentState,
      loading: true,
    });
    setVersion((v) => v + 1); // Trigger re-render

    const machineryTranslations = await fetchGPTTransform(
      mt.original,
      mt.translation,
      characteristic,
      localeName,
    );
    if (machineryTranslations.length > 0) {
      stateRef.current.set(mt, {
        loading: false,
        selectedOption: characteristic,
        llmTranslations: {
          ...currentState.llmTranslations,
          [characteristic]: machineryTranslations[0].translation,
        },
      });
    } else {
      stateRef.current.set(mt, {
        ...currentState,
        loading: false,
      });
    }
    setVersion((v) => v + 1);
  };

  const restoreOriginal = (mt: MachineryTranslation) => {
    const currentState = getSelState(mt);
    stateRef.current.set(mt, {
      ...currentState,
      selectedOption: '',
      llmTranslations: {},
    });
    setVersion((v) => v + 1);
  };
  return (
    <LLMTranslationContext.Provider
      value={{ getSelState, transformLLMTranslation, restoreOriginal }}
    >
      {children}
    </LLMTranslationContext.Provider>
  );
};

export const useLLMTranslation = (mt: MachineryTranslation) => {
  const { getSelState, transformLLMTranslation, restoreOriginal } = useContext(
    LLMTranslationContext,
  );
  return { ...getSelState(mt), transformLLMTranslation, restoreOriginal };
};
