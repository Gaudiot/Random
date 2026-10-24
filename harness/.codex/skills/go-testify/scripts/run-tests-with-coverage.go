//go:build ignore

package main

import (
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
)

var totalCoveragePattern = regexp.MustCompile(`(?m)^total:\s+\(statements\)\s+([0-9.]+%)\s*$`)

func main() {
	packages := os.Args[1:]
	if len(packages) == 0 {
		packages = []string{"./..."}
	}

	temporaryDirectory, err := os.MkdirTemp("", "go-test-coverage-")
	if err != nil {
		fmt.Fprintf(os.Stderr, "create temporary coverage directory: %v\n", err)
		os.Exit(1)
	}
	defer os.RemoveAll(temporaryDirectory)

	coverageProfile := filepath.Join(temporaryDirectory, "coverage.out")
	testArguments := []string{"test", "-covermode=atomic", "-coverprofile=" + coverageProfile}
	testArguments = append(testArguments, packages...)

	fmt.Printf("Running: go %v\n", testArguments)
	testCommand := exec.Command("go", testArguments...)
	testCommand.Stdout = os.Stdout
	testCommand.Stderr = os.Stderr
	testCommand.Stdin = os.Stdin
	testErr := testCommand.Run()

	coverageErr := printCoverage(coverageProfile)
	if testErr != nil {
		var exitError *exec.ExitError
		if errors.As(testErr, &exitError) {
			os.Exit(exitError.ExitCode())
		}
		fmt.Fprintf(os.Stderr, "run Go tests: %v\n", testErr)
		os.Exit(1)
	}
	if coverageErr != nil {
		fmt.Fprintf(os.Stderr, "report Go coverage: %v\n", coverageErr)
		os.Exit(1)
	}
}

func printCoverage(coverageProfile string) error {
	if profile, err := os.Stat(coverageProfile); err != nil || profile.Size() == 0 {
		if err != nil {
			return fmt.Errorf("coverage profile unavailable: %w", err)
		}
		return errors.New("coverage profile is empty")
	}

	coverageCommand := exec.Command("go", "tool", "cover", "-func="+coverageProfile)
	output, err := coverageCommand.CombinedOutput()
	if len(output) > 0 {
		fmt.Printf("\nCoverage by function:\n%s", output)
	}
	if err != nil {
		return err
	}

	match := totalCoveragePattern.FindSubmatch(output)
	if len(match) != 2 {
		return errors.New("total coverage percentage not found in go tool cover output")
	}

	fmt.Printf("\nTotal coverage: %s\n", match[1])
	return nil
}
