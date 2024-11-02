export type LlmConnection = {
    apiKey: string;
    model: LlmModels;
}

export enum LlmModels {
    'gpt4o' = 'gpt4o',
    'gpt4omini' = 'gpt4omini',
}