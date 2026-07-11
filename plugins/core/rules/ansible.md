---
paths:
  - "trading-servers/ansible/**/*.yaml"
  - "trading-servers/ansible/**/*.yml"
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
---

# Ansible Conventions

## Project

- Roles: `trading-servers/ansible/roles/`
- Always use FQCN for all modules (`ansible.builtin.apt`, not `apt`)
- Use `ansible.builtin.package` for installing packages (not `ansible.builtin.apt` or `ansible.builtin.yum`)
- Explicitly set `state: present` or `state: absent` even when optional
- Avoid `shell`, `command`, `raw` — use idempotent modules; if unavoidable, add `creates:` or `removes:`
- Set `become: true` at task level, not play level (unless all tasks in a play need it)

## Naming

- Every play, block, and task must have a `name`
- Start with action verb (Install, Configure, Copy...), capitalize first letter, no trailing period
- **Omit the role name** from role tasks — Ansible displays it automatically
- When including tasks from a file, prefix: `<TASK_FILENAME> : <TASK_NAME>`

## Play Order

1. `hosts`
2. Host options alphabetically (`become`, `remote_user`, `vars`)
3. `pre_tasks` → `roles` → `tasks`

## Task Order

1. `name`
2. Module declaration + parameters (multi-line map)
3. Loop operators (`loop`)
4. Task options alphabetically (`become`, `ignore_errors`, `register`)
5. `tags`

## Style

- 2-space indentation, always indent lists
- Blank line between host blocks, task blocks, and host/include blocks
- `snake_case` for variables, sorted alphabetically in `vars:` and variable files
- Always multi-line map syntax (even for single key-value)
- Single quotes by default; double quotes only inside single quotes or for escape sequences (`\n`)
- Long strings: `>` (folded) or `|` (literal) block scalar — no quoting
- File permissions: symbolic format only (`mode: u=rw,g=r,o=r`), not octal
- Quote filenames in `include` statements

## Example Task

```yaml
- name: Install required packages
  ansible.builtin.package:
    name: "{{ item }}"
    state: present
  loop: "{{ required_packages }}"
  become: true
  tags:
    - packages
```

## Linting

- Before completing work, run: `ansible-lint <changed-files>`
- Syntax check: `ansible-playbook --syntax-check <playbook>`
- Dry-run: `ansible-playbook --check --diff <playbook>`
