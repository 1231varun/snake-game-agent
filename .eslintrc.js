module.exports = {
  env: {
    browser: true,
    es2021: true
  },
  extends: 'standard',
  overrides: [
    {
      env: {
        node: true
      },
      files: [
        '.eslintrc.{js,cjs}'
      ],
      parserOptions: {
        sourceType: 'script'
      }
    }
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  rules: {
    'space-before-function-paren': ['error', 'never'],
    'semi': ['error', 'always'],
    'no-unused-vars': ['warn'],
    'no-var': ['error'],
    // Allow use of template literals in console.log
    'no-console': ['warn', { allow: ['warn', 'error'] }]
  }
} 