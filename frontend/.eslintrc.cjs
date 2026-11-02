module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    "eslint:recommended",
    "plugin:vue/vue3-essential",
  ],
  ignorePatterns: ["dist/", "node_modules/"],
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
  },
}
