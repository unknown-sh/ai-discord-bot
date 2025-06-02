// Modern ESLint config for React + JSX + Accessibility
import jsxA11y from "eslint-plugin-jsx-a11y";
import react from "eslint-plugin-react";
import babelParser from "@babel/eslint-parser";

export default [
  {
    files: ["src/**/*.{js,jsx}"],
    languageOptions: {
      parser: babelParser,
      parserOptions: {
        requireConfigFile: false,
        babelOptions: { presets: ["@babel/preset-react"] }
      },
      ecmaVersion: 2022,
      sourceType: "module",
      globals: { React: "readonly" }
    },
    plugins: {
      react,
      "jsx-a11y": jsxA11y
    },
    rules: {
      "react/jsx-uses-react": "off",
      "react/react-in-jsx-scope": "off",
      "react/prop-types": "off",
      "jsx-a11y/anchor-is-valid": "warn",
      "jsx-a11y/alt-text": "warn",
      "jsx-a11y/no-autofocus": "warn",
      "jsx-a11y/no-static-element-interactions": "warn",
      "no-unused-vars": "warn",
      "semi": ["error", "always"],
      "quotes": ["error", "double"]
    }
  }
];
