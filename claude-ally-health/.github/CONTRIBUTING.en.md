# Contributing Guidelines

Thank you for your interest in the Claude-Ally-Health project! We welcome contributions in any form.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Reporting Issues](#reporting-issues)
- [Submitting Code](#submitting-code)
- [Coding Standards](#coding-standards)
- [Commit Message Convention](#commit-message-convention)

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our code of conduct:

- Respect differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## 🚀 How to Contribute

### Reporting Bugs

This is a very helpful way to contribute to the project. If you encounter issues during use:

1. Check [Issues](https://github.com/huifer/Claude-Ally-Health/issues) to ensure the problem hasn't been reported
2. If you don't find a related issue, create a new one
3. Use the bug report template and provide as much detail as possible
4. Include reproduction steps, expected behavior, and actual behavior

### Suggesting New Features

If you have ideas for new features:

1. Discuss in [Issues](https://github.com/huifer/Claude-Ally-Health/issues) first
2. Explain the use case and why this feature would be useful
3. If you receive positive feedback, you can start implementing

### Submitting Code

We welcome Pull Requests! Here's how to get started:

## 🔧 Submitting Code

### Development Workflow

1. **Fork the Project**
   ```bash
   # Click the Fork button on GitHub
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Claude-Ally-Health.git
   cd Claude-Ally-Health
   ```

3. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # Or fix a bug
   git checkout -b fix/your-bug-fix
   ```

4. **Make Changes**
   - Follow the project's coding standards
   - Add necessary tests
   - Update relevant documentation

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "type: description"
   ```

6. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**
   - Create a Pull Request on GitHub
   - Fill out the PR template
   - Wait for code review

### Branch Naming

Use clear branch naming conventions:

- `feature/` - New features
  ```bash
  feature/add-blood-pressure-tracking
  ```
- `fix/` - Bug fixes
  ```bash
  fix/fix-date-parsing-error
  ```
- `docs/` - Documentation updates
  ```bash
  docs/update-readme-installation
  ```
- `refactor/` - Code refactoring
  ```bash
  refactor/optimize-data-structure
  ```
- `test/` - Test related
  ```bash
  test/add-unit-tests-for-medication
  ```

## 📝 Coding Standards

### File Organization

- Keep file structure clear and modular
- Use meaningful file and directory names
- Related functionality should be organized together

### Code Style

- **Consistency**: Maintain consistency with the existing project code style
- **Comments**: Add comments for complex logic
- **Naming**: Use clear, descriptive variable and function names
- **Simplicity**: Avoid unnecessary complexity and redundant code

### Documentation

- Update relevant Markdown documentation
- Add usage examples for new features
- Maintain bilingual style (Chinese and English) to match project standards

## 💬 Commit Message Convention

We use semantic commit messages with the following format:

```
<type>(<scope>): <subject>
```

### Type Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation update
- `style`: Code formatting (changes that don't affect code execution)
- `refactor`: Refactoring (neither new feature nor fix)
- `perf`: Performance optimization
- `test`: Testing related
- `chore`: Changes to build process or auxiliary tools
- `ci`: CI configuration files and script changes

### Scope

Specify the scope of the commit's impact, for example:

- `profile`: User profile
- `medication`: Medication management
- `radiation`: Radiation management
- `consult`: Consultation system
- `docs`: Documentation

### Subject

A brief summary describing the change:

- Use imperative mood, present tense: "change" not "changed" nor "changes"
- First letter lowercase
- Don't end with a period

### Examples

```bash
feat(medication): add drug interaction checking
fix(radiation): correct dose calculation for children
docs(readme): update installation instructions
refactor(data): optimize json structure for better performance
```

## 🧪 Testing

- Add tests for new features
- Ensure all tests pass
- Manually test critical functionality

## 📧 Contact

If you have any questions, please contact us through:

- Create a [GitHub Issue](https://github.com/huifer/Claude-Ally-Health/issues)
- Visit [WellAlly Tech](https://www.wellally.tech/)

## ⚖️ License

By contributing code, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

---

Thank you again for your contribution! 🎉
