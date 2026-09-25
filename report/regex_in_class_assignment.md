# In-Class Assignment
- Write the regex for:
	1. Names - Must start with a capital letter and only include lowercase letters afterward.
	2. Phone Numbers - Must be of the form (xxx)xxx-xxxx, where x is a digit. 
	3. Strings - Start with " and ends with "
	4. Any number in the language - Digits Dot Digits or Digits



# 1. Names
- `[A-Z][a-z]*`

# 2. Phone Numbers
- `\(\d{3}\)\d{3}-\d{4}`

# 3. Strings
- `"[^"]*"`

# 4. Numbers
- `\d+(\.\d+)?`

