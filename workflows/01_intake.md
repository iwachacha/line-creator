# 01 Intake

Input: user idea, intended product kind, language, desired count, target users, usage scenes, and rights notes.

Output: completed `brief.md`, initial `project.yml`, and HAG-1/HAG-2 review notes or automated QA rationale.

Approval gate: in manual mode, stop at HAG-1 and HAG-2 until the user confirms concept and rights risk. In automated mode, proceed when `project.yml` explicitly sets `automation.approval_policy: automated` and record the concept/risk rationale.

Before packaging, `project.yml` must contain non-empty LINE metadata:

- `creator_name`
- `title`
- `description`
- `copyright`

These fields are validated against the active LINE rule file for the project kind. Keep metadata original, non-advertising, URL-free, and consistent with the item list.

Failure return: if the idea depends on third-party IP, celebrity likeness, advertising, or prohibited motifs, revise the concept before continuing.
