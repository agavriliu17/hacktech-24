export type LlmConnection = {
    apiKey: string;
    model: LlmModels;
}

export enum LlmModels {
    'gpt4o' = 'gpt-4o',
    'gpt4omini' = 'gpt-4o-mini',
}