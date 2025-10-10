# Time_Warp IDE - PILOT Language Extended Commands Documentation

## Overview
The Time_Warp IDE now includes extended PILOT language commands for advanced functionality including file I/O, web operations, database access, string processing, and date/time operations.

## File I/O Commands (F:)

### F:READ filename variable_name [encoding]
Reads the entire contents of a file into a variable.
- `filename`: Path to the file to read
- `variable_name`: Variable to store the file contents
- `encoding`: Optional encoding (default: utf-8)
- Sets `FILE_READ_SUCCESS` (1=success, 0=failure) and `FILE_READ_SIZE`

Example: `F:READ data.txt CONTENT`

### F:WRITE filename content [encoding]
Writes content to a file (overwrites existing content).
- `filename`: Path to the file to write
- `content`: Text content to write (variables are resolved)
- `encoding`: Optional encoding (default: utf-8)
- Sets `FILE_WRITE_SUCCESS` and `FILE_WRITE_SIZE`

Example: `F:WRITE output.txt "Hello World"`

### F:APPEND filename content [encoding]
Appends content to an existing file.
- Sets `FILE_APPEND_SUCCESS` and `FILE_APPEND_SIZE`

Example: `F:APPEND log.txt "New log entry"`

### F:DELETE filename
Deletes a file from the filesystem.
- Sets `FILE_DELETE_SUCCESS`

Example: `F:DELETE temp.txt`

### F:EXISTS filename variable_name
Checks if a file exists.
- Stores 1 (exists) or 0 (doesn't exist) in the variable

Example: `F:EXISTS config.ini CONFIG_EXISTS`

### F:SIZE filename variable_name
Gets the size of a file in bytes.
- Stores -1 if file doesn't exist or error occurs

Example: `F:SIZE data.bin FILE_SIZE`

### F:LIST directory [pattern]
Lists files in a directory matching an optional pattern.
- `pattern`: Glob pattern (default: "*")
- Sets `FILE_LIST_COUNT`

Example: `F:LIST /home/user *.txt`

## Web/HTTP Commands (W:)

### W:GET url variable_name [timeout]
Downloads content from a URL using HTTP GET.
- `timeout`: Timeout in seconds (default: 10)
- Sets `WEB_GET_SUCCESS`, `WEB_GET_SIZE`, `WEB_LAST_URL`

Example: `W:GET https://api.example.com/data RESPONSE`

### W:POST url data variable_name [content_type] [timeout]
Sends data to a URL using HTTP POST.
- `content_type`: MIME type (default: application/x-www-form-urlencoded)
- Sets `WEB_POST_SUCCESS`, `WEB_POST_SIZE`, `WEB_LAST_URL`

Example: `W:POST https://api.example.com/submit "name=John&age=25" RESULT`

### W:DOWNLOAD url filename [timeout]
Downloads a file from a URL and saves it locally.
- `timeout`: Timeout in seconds (default: 30)
- Sets `WEB_DOWNLOAD_SUCCESS`, `WEB_DOWNLOAD_SIZE`

Example: `W:DOWNLOAD https://example.com/file.pdf document.pdf`

### W:ENCODE text variable_name [encoding_type]
Encodes text using various encoding schemes.
- `encoding_type`: url, base64, or html (default: url)

Example: `W:ENCODE "Hello World!" ENCODED url`

### W:DECODE text variable_name [encoding_type]
Decodes previously encoded text.

Example: `W:DECODE "Hello%20World%21" DECODED url`

## Database Commands (D:)
Provides SQLite database operations.

### D:OPEN database_file
Opens a connection to a SQLite database file.
- Creates the file if it doesn't exist
- Sets `DB_CONNECTED` and `DB_FILE`

Example: `D:OPEN mydata.db`

### D:CLOSE
Closes the current database connection.
- Sets `DB_CONNECTED` to 0

### D:EXECUTE sql_statement
Executes a SQL statement (INSERT, UPDATE, DELETE, CREATE, etc.).
- Sets `DB_EXECUTE_SUCCESS` and `DB_ROWS_AFFECTED`

Example: `D:EXECUTE CREATE TABLE users (id INTEGER, name TEXT)`

### D:QUERY sql_statement variable_name
Executes a SELECT query and stores results.
- Results stored as comma-separated values, one row per line
- Sets `DB_QUERY_ROWS` and `DB_QUERY_COLS`

Example: `D:QUERY "SELECT * FROM users" USER_LIST`

### D:CREATE TABLE table_name columns
Creates a new table with specified columns.
- Sets `DB_CREATE_SUCCESS`

Example: `D:CREATE TABLE products "id INTEGER PRIMARY KEY, name TEXT, price REAL"`

### D:INSERT table_name values
Inserts a new row into a table.
- Sets `DB_INSERT_SUCCESS` and `DB_LAST_ROWID`

Example: `D:INSERT products "'Widget', 19.99'"`

## String Processing Commands (S:)

### S:LENGTH text variable_name
Gets the length of a string.

Example: `S:LENGTH "Hello World" TEXT_LEN`

### S:UPPER text variable_name
Converts text to uppercase.

Example: `S:UPPER "hello" UPPER_TEXT`

### S:LOWER text variable_name
Converts text to lowercase.

Example: `S:LOWER "HELLO" LOWER_TEXT`

### S:SUBSTRING text start length variable_name
Extracts a substring starting at position `start` with `length` characters.

Example: `S:SUBSTRING "Hello World" 6 5 WORD`

### S:FIND text search variable_name
Finds the position of a substring in text (-1 if not found).

Example: `S:FIND "Hello World" "World" POS`

### S:REPLACE text old_text new_text variable_name
Replaces all occurrences of old_text with new_text.

Example: `S:REPLACE "Hello World" "World" "Universe" NEW_TEXT`

### S:SPLIT text delimiter variable_name
Splits text by delimiter, stores parts separated by newlines.
- Sets `{variable_name}_COUNT` with number of parts

Example: `S:SPLIT "apple,banana,cherry" "," FRUITS`

### S:TRIM text variable_name
Removes leading and trailing whitespace.

Example: `S:TRIM "  Hello World  " CLEAN_TEXT`

### S:REGEX operation parameters
Regular expression operations:
- `S:REGEX MATCH text pattern variable_name` - Find first match
- `S:REGEX REPLACE text pattern replacement variable_name` - Replace matches
- Sets `{variable_name}_FOUND` for MATCH operation

Example: `S:REGEX MATCH "Email: user@domain.com" "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" EMAIL`

### S:FORMAT template variable_name [arg1] [arg2] ...
Formats a template string with arguments using Python format syntax.

Example: `S:FORMAT "Hello {0}, you are {1} years old" GREETING "John" "25"`

## Date/Time Commands (DT:)

### DT:NOW variable_name [format]
Gets current date/time.
- `format`: strftime format string (default: "%Y-%m-%d %H:%M:%S")
- Also sets `DT_YEAR`, `DT_MONTH`, `DT_DAY`, `DT_HOUR`, `DT_MINUTE`, `DT_SECOND`

Example: `DT:NOW CURRENT_TIME "%Y-%m-%d %H:%M"`

### DT:FORMAT date_string input_format output_format variable_name
Converts date string from one format to another.

Example: `DT:FORMAT "2024-01-15" "%Y-%m-%d" "%B %d, %Y" FORMATTED_DATE`

### DT:ADD date_string format days hours minutes variable_name
Adds time to a date.

Example: `DT:ADD "2024-01-15 10:30:00" "%Y-%m-%d %H:%M:%S" 7 2 30 NEW_DATE`

### DT:DIFF date1 date2 format variable_name [unit]
Calculates difference between two dates.
- `unit`: days, hours, minutes, or seconds (default: days)

Example: `DT:DIFF "2024-01-01" "2024-01-15" "%Y-%m-%d" DAYS_DIFF`

### DT:PARSE date_string format variable_prefix
Parses a date into separate components.
- Creates variables: `{prefix}_YEAR`, `{prefix}_MONTH`, `{prefix}_DAY`, etc.

Example: `DT:PARSE "2024-01-15 14:30:45" "%Y-%m-%d %H:%M:%S" PARSED`

### DT:TIMESTAMP variable_name [date_string] [format]
Gets Unix timestamp (seconds since epoch).
- Without parameters: current timestamp
- With parameters: timestamp for specific date

Example: `DT:TIMESTAMP CURRENT_TIMESTAMP`

## Variable Resolution

All command parameters support variable resolution using existing PILOT variable syntax. Variables are automatically resolved before command execution.

## Error Handling

All commands set appropriate success/failure variables and log errors to the output. Commands continue execution even on errors to maintain program flow.

## Examples

See `pilot_feature_test.pilot` for comprehensive examples of all new features.