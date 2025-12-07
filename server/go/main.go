package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/hashicorp/terraform-exec/tfexec"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

type Input struct {
	Code string `json:"code" jsonschema:"The raw terraform configuration string to validate"`
}

type Output struct {
	IsValid bool   `json:"is_valid" jsonschema:"true if the terraform code is valid"`
	Report  string `json:"report" jsonschema:"detailed validation results or error messages"`
}

func TfValidate(ctx context.Context, req *mcp.CallToolRequest, input Input) (*mcp.CallToolResult, Output, error) {
	// terraform requires a directory context to run init/validate.
	tmpDir, err := os.MkdirTemp("", "tf-validate-*")
	if err != nil {
		return nil, Output{IsValid: false, Report: fmt.Sprintf("System error creating temp dir: %s", err)}, nil
	}
	defer os.RemoveAll(tmpDir)

	tfFile := filepath.Join(tmpDir, "main.tf")
	if err := os.WriteFile(tfFile, []byte(input.Code), os.FileMode(0644)); err != nil {
		return nil, Output{IsValid: false, Report: fmt.Sprintf("System error writing file: %s", err)}, nil
	}

	execPath, err := exec.LookPath("terraform")
	if err != nil {
		return nil, Output{IsValid: false, Report: "Terraform binary not found on the server path."}, nil
	}

	tf, err := tfexec.NewTerraform(tmpDir, execPath)
	if err != nil {
		return nil, Output{IsValid: false, Report: fmt.Sprintf("Failed to load terraform wrapper: %s", err)}, nil
	}

	// run terraform init
	err = tf.Init(ctx, tfexec.Upgrade(true))
	if err != nil {
		return nil, Output{
			IsValid: false,
			Report:  fmt.Sprintf("Terraform init failed:\n%s", err),
		}, nil
	}

	// run terraform validate
	result, err := tf.Validate(ctx)
	if err != nil {
		return nil, Output{IsValid: false, Report: fmt.Sprintf("Terraform validate failed:\n%s", err)}, nil
	}

	if result.Valid {
		return nil, Output{IsValid: true, Report: "Configuration is valid."}, nil
	}

	// construct a readable error report
	var report strings.Builder
	report.WriteString("Validation Failed:\n")
	for _, diag := range result.Diagnostics {
		report.WriteString(fmt.Sprintf("- [%s] %s: %s", diag.Severity, diag.Summary, diag.Detail))
		if diag.Range != nil {
			report.WriteString(fmt.Sprintf(" (Line: %d)", diag.Range.Start.Line))
		}
		report.WriteString("\n")
	}

	return nil, Output{IsValid: false, Report: report.String()}, nil
}

func main() {
	server := mcp.NewServer(&mcp.Implementation{
		Name:    "Demo",
		Version: "0.1.0",
	}, &mcp.ServerOptions{})

	mcp.AddTool(server, &mcp.Tool{
		Name:        "tf_validate",
		Description: "Validates a string of Terraform HCL code. Returns true if valid, or a list of syntax/configuration errors.",
	}, TfValidate)

	if err := server.Run(context.Background(), &mcp.StdioTransport{}); err != nil {
		log.Fatal(err)
	}
}
