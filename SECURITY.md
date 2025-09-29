# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in `krishnaharshap/vin-lookup-test-framework`, please follow a responsible disclosure process:

- **Do not create a public issue**. Instead, report vulnerabilities by opening a [GitHub Security Advisory](https://docs.github.com/en/code-security/security-advisories) or email the maintainers directly if contact information is available.
- Provide as much detail as possible to help us quickly identify and resolve the issue.
- We will review and address all reports as soon as possible.

## Security Features

This repository utilizes GitHub’s built-in security tools to help protect contributors and users:

- **Dependabot alerts**: Automated alerts for vulnerable dependencies.
- **Security advisories**: Private discussions and coordinated disclosure/fixes for vulnerabilities.
- **Code scanning**: Automated scanning for vulnerabilities and code errors.
- **Secret scanning**: Detection and blocking of tokens, credentials, and secrets before they are pushed.

For more information, see [GitHub security features](https://docs.github.com/en/code-security).

## Keeping Sensitive Data Out of the Repository

- Ensure sensitive files are listed in `.gitignore` to avoid accidental commits.
- Do not commit API keys, secrets, or private configuration files.
- If sensitive data is inadvertently committed, notify the maintainers so it can be removed from the repository history.

## Branch Protection Rules

We recommend maintaining branch protection policies to:

- Require pull request reviews before merging.
- Ensure all status checks (builds, linters, tests) pass before merging.
- Protect the main and release branches from direct pushes.

## Security Best Practices

- Regularly check for dependency updates and security patches.
- Use automated tools for code quality and vulnerability detection.
- Follow safe coding and operational practices throughout the software development lifecycle.

## References

- [Adding a security policy to your repository](https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository)
- [About repository security advisories](https://docs.github.com/en/code-security/security-advisories/about-security-advisories)
- [Using .gitignore to keep sensitive files out of your repo](https://git-scm.com/docs/gitignore)
- [About branch protection rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/protecting-branches)

---

By following these guidelines, we help ensure a safer and more secure codebase for everyone.
