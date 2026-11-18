/**
 * THIS FILE WAS CREATED VIA CODEGEN DO NOT MODIFY {@see http://go/af-codegen}
 *
 * Metadata for generation of `@atlaskit/ads-mcp` and https://atlassian.design/llms-tokens.txt.
 *
 * @codegen <<SignedSource::e2a0fe15e0c6ce2a9d3e08f1e527bf55>>
 * @codegenCommand yarn build tokens
 */
export interface Token {
    name: string;
    path: string[];
    description: string;
    exampleValue?: string | number;
    usageGuidelines: {
        usage: string;
        cssProperties: string[];
    };
}
export declare const tokens: Token[];
