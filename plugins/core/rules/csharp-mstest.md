---
paths:
  - "**/*.Tests/**/*.cs"
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
---

# MSTest Best Practices

Write effective unit tests with MSTest, covering both standard and data-driven testing approaches.

## Project Setup

- Use a separate test project with naming convention `[ProjectName].Tests`
- Reference MSTest package
- Create test classes that match the classes being tested (e.g., `CalculatorTests` for `Calculator`)

## Test Structure

- Use `[TestClass]` attribute for test classes
- Use `[TestMethod]` attribute for test methods
- Follow the Arrange-Act-Assert (AAA) pattern
- Name tests using the pattern `MethodName_Scenario_ExpectedBehavior`:
  - Good: `ParseDate_InvalidFormat_ThrowsFormatException`
  - Bad: `TestParsing`, `Test1`
- Use `[TestInitialize]` and `[TestCleanup]` for per-test setup and teardown
- Use `[ClassInitialize]` and `[ClassCleanup]` for per-class setup and teardown
- For async test methods, always return `Task`, never use `async void`

## Standard Tests

- Keep tests focused on a single behavior
- Avoid testing multiple behaviors in one test method
- Use clear assertions that express intent
- Include only the assertions needed to verify the test case
- Make tests independent and idempotent (can run in any order)

## Data-Driven Tests

- Use `[TestMethod]` combined with data source attributes
- Use `[DataRow]` for inline test data
- Use `[DynamicData]` for programmatically generated test data
- Use meaningful parameter names in data-driven tests

## Assertions

- Before writing assertions, check the existing test project for which assertion style is used:
  - **FluentAssertions** (`.Should()`) — e.g., `result.Should().Be(42)`, `act.Should().Throw<T>()`
  - **MSTest Assert** — e.g., `Assert.AreEqual(42, result)`, `Assert.ThrowsException<T>(act)`
- Match the assertion style already used in the test project. Do not mix styles.
- If the project uses both styles (mixed) or is a brand new test project with no existing tests, ask the user which style to use.

## Mocking and Isolation

- Use Moq for mocking dependencies
- Mock dependencies to isolate units under test
- Use interfaces to facilitate mocking

## Test Organization

- Group tests by feature or component
- Use test categories with `[TestCategory("Category")]` to organize test runs
