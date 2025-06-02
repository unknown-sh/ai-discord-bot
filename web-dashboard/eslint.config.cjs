// Modern ESLint config for React + JSX + Accessibility (CJS for ESLint 9+)
module.exports = [
  {
    files: ["src/**/*.{js,jsx}"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: { React: "readonly" }
    },
    plugins: {
      react: require("eslint-plugin-react"),
      jsxA11y: require("eslint-plugin-jsx-a11y")
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
