# Commit Messages

## Review Process
When asked to commit changes, always review **both**:
- **Unstaged changes** (modified tracked files shown in `git diff`)
- **Untracked files** (new files not yet added to git)

Present a summary of all changes and confirm with the user which files to include before committing.

## Format
Always format commit messages using the **Conventional Commits** format:
`type(scope): description`

## Allowed Types
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools and libraries (e.g., config files, composer/npm updates)

## Scopes
Use scopes to describe the module or feature affected (optional but recommended).
Examples:
- `importer`
- `dol:download`
- `dol:process`
- `ui`
- `auth`

## Description
- Use the imperative, present tense: "change" not "changed" nor "changes"
- Don't capitalize the first letter
- No dot (.) at the end

## Co-Authorship
Do NOT include a "Co-Authored-By" line in commit messages.

## Examples
- `feat(auth): add google login support`
- `fix(importer): handle null values in schedule A`
- `docs: update roadmap with new tasks`
