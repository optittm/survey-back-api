# Survey Report API

The Survey Report API is a web application that generates reports based on survey project data. It provides endpoints to generate overall survey reports and detailed project reports.

## Usage

### Survey Report

- **Endpoint:** `/survey-report`
- **Method:** GET
- **Description:** Generates the survey report.

### Detailed Project Report

- **Endpoint:** `/survey-report/project/{id}`
- **Method:** GET
- **Description:** Generates the detailed project report for the specified project ID.
- **Parameters:**
  - `id`: The ID of the project.
  - `timerange` (optional): The time range for the report. Default is "week".
  - `timestamp_start` (optional): The start timestamp for filtering the rates.
  - `timestamp_end` (optional): The end timestamp for filtering the rates.

The detailed project report includes graphs with box plots, which provide insights into the distribution and statistical summary of the rates. The x-axis represents the timestamps, and the y-axis represents the rates.