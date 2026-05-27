# Security Policy

## 📢 Reporting Security Vulnerabilities

This project takes security seriously and we appreciate your responsible disclosure of vulnerabilities.

### Supported Versions

Currently, the following versions are receiving security updates:

| Version | Support Status |
|---------|----------------|
| Main branch (main) | ✅ Supported |
| Other versions | ❌ Unsupported |

### Reporting a Vulnerability

If you discover a security vulnerability, **please do NOT** create a public issue.

#### How to Report

Please report security vulnerabilities privately through the following methods:

1. **Send email to**: huifer97@163.com
2. **Email subject**: [Security] Claude-Ally-Health Security Vulnerability Report

#### Report Contents

Please include as much of the following information as possible:

- **Vulnerability Description**: Detailed description of the nature and location of the vulnerability
- **Affected Versions**: Which versions are affected
- **Reproduction Steps**: How to reproduce the vulnerability
- **Potential Impact**: Potential harm caused by the vulnerability
- **Suggested Fix**: If you have fix suggestions, please provide them

### Response Time

- We will acknowledge receipt of your report within **48 hours**
- Provide preliminary assessment and estimated fix time within **7 days**
- Notify you when the fix is complete

### Vulnerability Handling Process

1. **Confirmation**: Confirm the vulnerability and assess its severity
2. **Fix**: Develop and test the fix
3. **Release**: Create a security patch and release a new version
4. **Disclosure**: Publicly disclose in the changelog after the fix is complete

## 🔒 Security Best Practices

### Data Privacy

This project is a **locally running** personal medical data management system with the following security features:

#### ✅ Security Features

- **Local Storage**: All data is stored on the local file system
- **No Cloud Sync**: No uploads to any remote services
- **No External Database Dependencies**: Uses pure JSON file storage
- **Complete Privacy**: Users have complete control over their data

#### ⚠️ Usage Recommendations

1. **Access Control**
   - Ensure your computer account is secure
   - Use strong passwords and encryption
   - Regularly backup important data

2. **Data Backup**
   - Regularly backup the `data/` directory
   - Store backups in a secure location
   - Consider encrypting sensitive backups

3. **Environment Security**
   - Run the system in a trusted environment
   - Avoid using on public computers
   - Don't share files containing sensitive data

4. **Version Control**
   - Ensure `.gitignore` includes the `data/` directory
   - Don't commit files containing personal data to Git
   - Regularly check Git history to ensure no sensitive information

### AI Security

This project uses Claude Code and AI visual analysis, please note:

- **Reference Only**: AI analysis results are for reference only and not as a basis for medical diagnosis
- **Data Privacy**: Image recognition features may call external AI services (such as MCP servers)
- **Verify Recommendations**: For important information such as drug interactions, please consult professional medical personnel

## 🛡️ Common Security Issues

### The Following Are Known Non-Security Issues

- **Local Data Visibility**: Data is stored on the local file system, this is intentional
- **No Encryption**: Data is stored in JSON plain text, relying on operating system access controls

### The Following Are Security Issues

- **Unauthorized Access**: If your computer is compromised, data may be accessed
- **Data Loss**: Without backups, hardware failure may result in data loss
- **AI Service Privacy**: Image recognition features may involve external service calls

## 📋 Security Checklist

Before using this project, please ensure:

- [ ] Your operating system and software are updated to the latest versions
- [ ] Your computer account uses a strong password
- [ ] Disk encryption is enabled (such as BitLocker, FileVault)
- [ ] `.gitignore` is correctly configured to avoid committing sensitive data
- [ ] You have a regular backup strategy
- [ ] You understand the privacy implications of AI features

## 🔄 Updates and Security Patches

We commit to:

- Promptly fix known security vulnerabilities
- Label security-related changes in the changelog
- Support security updates for older versions within a reasonable time
- Notify users of important security issues

## 📧 Contact

For security issues or suggestions, please contact:

- **Email**: huifer97@163.com
- **GitHub Issues**: [https://github.com/huifer/Claude-Ally-Health/issues](https://github.com/huifer/Claude-Ally-Health/issues) (for non-security issues only)

---

Thank you for helping us keep our users safe! 🔒
