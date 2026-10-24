---

## name: go-testify

description: Create or update Go unit tests in repositories that use Testify, while preserving the project's established Go testing conventions. Use for changed Go behavior that benefits from isolated unit coverage; not for integration-only wiring or generated code.

# Go Unit Tests with Testify

Use this skill only after inspecting the repository instructions, current diff, `go.mod`, test commands, and nearby `*_test.go` files. Local conventions take precedence over this guidance.

## Test design

- Place tests beside the code under test unless the project consistently uses an external test package or another layout.
- Follow the repository's package choice (`package foo` versus `package foo_test`) and existing file naming conventions.
- Create one top-level test function for each production function or method under test, named `Test<FunctionName>` (for example, `TestCreateUser`). Keep every scenario for that function inside this top-level test.
- Start each scenario with `t.Run("Scenario name", func(t *testing.T) { ... })`. Do not put a test case directly in the body of `Test<FunctionName>`.
- A scenario may be table-driven when several cases share the same arrangement, action, and assertions. Keep the table inside the relevant `t.Run`; each table row must run as its own nested `t.Run`. Use separate scenarios when their setup or expected behavior differs enough that a table would obscure intent.
- Exercise observable behavior, exported contracts, meaningful branches, validation rules, error propagation, and boundary cases introduced or affected by the current change.
- Prefer a `setupTest(t *testing.T)` helper that calls `t.Helper()`, constructs a fresh system under test (`sut`), creates fresh mocks, injects those mocks, and returns them to the caller. Call it inside each scenario—or inside each nested table-row subtest—so no SUT or mutable mock instance is shared between cases. If the package already has a conflicting helper name, use the repository's equivalent scoped name while preserving the same isolation.
- Keep scenario-specific fixtures and mock expectations in the scenario that uses them. Do not store mutable SUTs or mocks in package-level variables.
- Use `t.Cleanup` for cleanup and avoid shared mutable fixtures across parallel tests.
- Use `t.Parallel()` only when the surrounding suite does so and the test has no shared state, mock, environment, database, filesystem, or ordering dependency.



## Assertions

- Use `require` when a failed condition makes later assertions unsafe or meaningless; use `assert` when independent checks should continue.
- Prefer semantic assertions such as `require.ErrorIs`, `require.ErrorAs`, `require.NoError`, `require.Equal`, `require.Nil`, and `require.NotNil` over manual conditionals.
- Put expected values before actual values in Testify calls: `require.Equal(t, expected, actual)`.
- Assert the result and externally visible side effects, not incidental implementation details.



## Testify mocks

- Mock interfaces at process or dependency boundaries rather than concrete internals.
- Configure only interactions relevant to the scenario. Use `.Once()` when exactly one call is part of the contract.
- Prefer precise arguments or `mock.MatchedBy` when argument content matters; use `mock.Anything` only when that argument is irrelevant to the behavior under test.
- Verify expected calls with the project's established approach, such as `AssertExpectations(t)`. Assert zero calls for collaborators that must not run on validation or early-error paths.
- Create fresh mocks per test or subtest. Never share mutable Testify mocks across parallel tests.



## Scope and validation

- Do not unit-test thin routers, `main`, SDK pass-through wiring, generated mocks, or trivial constructors unless they contain meaningful custom behavior.
- Do not add Testify if the repository intentionally uses only Go's standard testing package or another established framework.
- Format changed Go files with `gofmt` and run the narrow package test first (for example, `go test ./path/to/package`).
- Resolve this skill's absolute directory from the loaded `SKILL.md`, then use its bundled coverage tool from the target repository root to run the broader applicable tests and display per-function and total statement coverage. Do not assume the skill is stored inside the repository:

  ```text
  go run <absolute-go-testify-skill-directory>/scripts/run-tests-with-coverage.go ./...
  ```

  Replace `./...` with one or more package patterns for a narrower run. With no package arguments, the tool defaults to `./...`. It writes the coverage profile to a temporary directory, removes it afterward, and preserves a failing `go test` exit code. Treat the percentage as diagnostic evidence, not a coverage target; prioritize meaningful behavioral assertions over increasing the number.
- Report the exact test command, result, total coverage percentage when available, and any race, environment, or pre-existing failures accurately.
