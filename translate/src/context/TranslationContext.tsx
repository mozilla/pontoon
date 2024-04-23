import React, { createContext, useContext, useEffect, useState } from 'react';
import { type MachineryTranslation, fetchGPTTransform } from '~/api/machinery';
import { useActiveTranslation } from './EntityView';

type SelState = {
  loading: boolean;
  selectedOption: string;
  llmTranslation: string;
};

interface LLMTranslationContextType {
  getSelState(mt: MachineryTranslation): SelState;
  transformLLMTranslation: (
    mt: MachineryTranslation,
    characteristic: string,
    localeName: string,
  ) => Promise<void>;
}

const initSelState = () => ({
  loading: false,
  selectedOption: '',
  llmTranslation: '',
});

const LLMTranslationContext = createContext<LLMTranslationContextType>({
  getSelState: initSelState,
  transformLLMTranslation: async () => {},
});

export const LLMTranslationProvider: React.FC = ({ children }) => {
  const translation = useActiveTranslation();
  const [state, setState] = useState(new Map<MachineryTranslation, SelState>());

  useEffect(() => setState(new Map()), [translation]);

  const getSelState = (mt: MachineryTranslation) =>
    state.get(mt) ?? initSelState();

  const transformLLMTranslation = async (
    mt: MachineryTranslation,
    characteristic: string,
    localeName: string,
  ) => {
    let { llmTranslation, selectedOption } = getSelState(mt);
    if (characteristic !== 'original') {
      let next = new Map(state);
      next.set(mt, { loading: true, selectedOption, llmTranslation });
      setState(next);
      const machineryTranslations = await fetchGPTTransform(
        mt.original,
        mt.translation,
        characteristic,
        localeName,
      );
      if (machineryTranslations.length > 0) {
        llmTranslation = machineryTranslations[0].translation;
        selectedOption = characteristic;
      }
      next = new Map(state);
      next.set(mt, { loading: false, selectedOption, llmTranslation });
      setState(next);
    } else {
      let next = new Map(state);
      next.delete(mt);
      setState(next);
    }
  };

  return (
    <LLMTranslationContext.Provider
      value={{ getSelState, transformLLMTranslation }}
    >
      {children}
    </LLMTranslationContext.Provider>
  );
};

export const useLLMTranslation = (mt: MachineryTranslation) => {
  const { getSelState, transformLLMTranslation } = useContext(
    LLMTranslationContext,
  );
  return { ...getSelState(mt), transformLLMTranslation };
};
