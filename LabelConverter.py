import os
import sys

usage = "Usage: {} AuSeq_[Song-Name].txt".format (sys.argv [0])
def print_usage ():
	print (usage) # One-liner function, I know, I know. I like abstraction, alright? Sue me.

CSV_DELIMITER       = ","
CSV_PAD_CHAR        = " "
CSV_PADDING_ENABLED = True

# Parameters:
# [""]   headers: a list of strings used as headers / column names for the CSV columns.
# [[""]] rows:    a nested list of strings used to store each row and its values for each column in the row.
# Returns:
# ""     out_csv: a string representation of the generated CSV, ready to be written to a file.
def make_csv (headers, rows, remove_trailing_newline = False):
	out_csv = ""
	out_csv += "{}\n".format (CSV_DELIMITER.join (headers))
	for row in rows:
		assert len (row) == len (headers), "{columns_we_have} columns in row {row_contents} where {necessary_column_count} were needed ({necessary_columns})!".format (columns_we_have = len (row), row_contents = row, necessary_column_count = len (headers), necessary_columns = headers)
		current_column = 0
		padded_columns = []
		for column in row:
			if CSV_PADDING_ENABLED: # Check if we should pad our columns with spaces.
				# We're assuming that all column values have string lengths less than or equal to the lengths of their subsequent headers.
				# This should be true in our case but may not always be true.
				padded_column = column.ljust (len (headers [current_column]), CSV_PAD_CHAR)
			else:
				padded_column = column
			padded_columns.append (padded_column)
			current_column += 1
		out_csv += "{}\n".format (CSV_DELIMITER.join (padded_columns))
	if remove_trailing_newline and out_csv.endswith ("\n"): # It does, because each new line that gets pushed has a newline at the end... whatever. Clarity.
		out_csv = out_csv [:-1] # Removes last character, "\n" in this case.
	return out_csv

if len (sys.argv) == 1:
	print ("No AuSeq file specified!")
	print_usage ()
	sys.exit (1)

in_filename = sys.argv [1]

if not os.path.exists (in_filename):
	print ("AuSeq file specified doesn't exist! Make sure the filename doesn't have spaces or other special characters.")
	print_usage ()
	sys.exit (1)

out_filename = in_filename [2:] # removes "Au" from front of string

labels = [] # Initialize an empty list for storage of labels

print ("--- PARSING INPUT FILE {} ---".format (in_filename))

with open (in_filename, "r") as in_file: # Open the input file for reading
	in_file_data = in_file.read () # Read the entirety of the input file into a string variable

in_file_lines = in_file_data.split ("\n") # Generate an array based on splitting the input file data on newline characters

for in_file_line in in_file_lines: # Iterate over the array of lines in the input file
	split_in_file_line = in_file_line.split ("\t") # Split the current line on tabulator characters, which is what Audacity uses as column delimiters
	labels.append (split_in_file_line) # Append the split current line to the list of labels

# Check for a trailing label due to a duplicate newline character
if labels [-1] == ['']: # Checks if the last entry in the labels list is equal to a list with one item, an empty string
	labels.pop (-1) # Remove the trailing label if it exists by popping it by index

print ("--- PARSING COMPLETE! ---")
print ("\n{}\n".format (labels))

GPIO_PIN_NUMBER = "5"
LED_ON_VALUE    = "1"
LED_OFF_VALUE   = "0"
END_CMD_NAME    = "END"

csv_rows = [] # Initialize an empty list for storage of rows that contain information about labels
for label in labels:
	start_time_s = float (label [0])
	end_time_s = float (label [1])
	start_time_ms_int = round (start_time_s * 1000)
	end_time_ms_int = round (end_time_s * 1000)
	csv_rows.append ([str (start_time_ms_int), GPIO_PIN_NUMBER, LED_ON_VALUE])
	csv_rows.append ([str (end_time_ms_int), GPIO_PIN_NUMBER, LED_OFF_VALUE])

END_MS_TIME_OFFSET = 100

# Add an "END" command to the end of the CSV. Who knows what this does? I don't. I'm just guessing it needs to be 100ms after the last LED is shut off based on the example.
csv_rows.append ([str (end_time_ms_int + END_MS_TIME_OFFSET), END_CMD_NAME, "1"])

out_csv = make_csv (["TIME(MS)", "COMMAND", "VALUE"], csv_rows, remove_trailing_newline = True) # I'm trying to model the output format after the format of the examples I was given, which didn't have trailing newlines for whatever reason. shruggie.

print ("--- GENERATED CSV: --- ")
print ("\n{}\n".format (out_csv))

print ("--- WRITING OUTPUT FILE {} ---".format (out_filename))

if os.path.exists (out_filename):
	if not input ("Output file {} exists! Type 'y' to confirm overwriting: ".format (out_filename)) == "y":
		print ("Not overwriting; exiting.")
		sys.exit (0)

with open (out_filename, "w+") as out_file:
	out_file.write (out_csv)

print ("--- DONE WRITING OUTPUT FILE ---")
print ("have a nice day :)")