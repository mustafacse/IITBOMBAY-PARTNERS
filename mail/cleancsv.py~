import csv
import sys

# This script will expext three arguments:
# 1. File with data to be scrubbed (CleanCsv.in_file)
# 2. File name to output clean data (CleanCsv.clean_out_file)
# 3. File name to output data that's needs review (CleanCsv.dirty_out_file)

class CleanCsv(object):
    def __init__(self, args):
        self.in_file = args[1]  # Storing original (necc?)
        self.clean_out_file = args[2]
        self.dirty_out_file = args[3]
        self.flags = [x for x in args[4:] if sys.argv != ""]
        # Unnecessary?  sys.argv will never be blank---> ^^^
        self.manual_repair = []
        self.rows = []
        self.functions = [
            'strip_blank_fields',
            'strip_whitespace',
            'capitalize',
            'strip_blank_lists',
            'split_on_blanks',
            'remove_duplicate_names',
            'remove_bad_rows',
            'columnize',
            ]

    def do_scrub(self):
        """Runs all functions in self.functions that weren't negated by command-
        line arguments.  Writes a clean file and, optionally, a file of rows
        that couldn't be properly scrubbed
        """
        self.fxns = [x for x in self.functions if x not in self.flags]
        self.grab_file_data(self.in_file)
        for fx in self.fxns:
            next_operation = getattr(self, fx)
            next_operation()
        if self.manual_repair:
            self.write_csv(self.manual_repair, self.dirty_out_file)
        self.write_csv(self.rows, self.clean_out_file)

    def grab_file_data(self, filename):
        """Opens the file passed as filename and writes rows to a list of lists.
        """
        with open(filename, 'rt') as opened_file:
            read_file = csv.reader(opened_file)
            for row in read_file: #  [q1]
                self.rows.append(row)
            opened_file.close

    def strip_blank_fields(self):
        """If there are any blank fields in a row, take them output.
        """
        for row in self.rows:
            while "" in row:
                row.remove("")

    def strip_whitespace(self):
        """If there is whitespace in a field, take it out."""
        for row in self.rows:
            for num, field in enumerate(row):
                row[num] = field.strip()

    def capitalize(self):
        """Make all non email fields capitalized (string.title()).
        """
        for row in self.rows:
            for num, field in enumerate(row):
                if "@" not in field and not field.istitle():
                    row[num] = field.title()

    def strip_blank_lists(self):
        """Remove any rows that are blank.
        """
        while [] in self.rows:
            self.rows.remove([])

    def split_on_blanks(self):
        """For fields that have a space between two words, split them out into
        seperate fields
        """
        for row in self.rows:
            for num, field in enumerate(row):
                if ' ' in field:
                    x = field.split(' ')
                    row.pop(num)
                    for i in x:
                        row.append(i)

        # Move all the emails addresses to the last column.
        for row in self.rows:
            for num, field in enumerate(row):
                if "@" in field:
                    x = row.pop(num)
                    row.append(x)

    def remove_duplicate_names(self):
        """If two columns have the same name in them, remove one of the names.
        """
        for num, row in (enumerate(self.rows)):
            for x in xrange(len(row)):
                if row.count(row[x]) > 1:
                    row.pop(x)
                    break

    def remove_bad_rows(self):
        """Remove all rows that don't have at least three fields filled.
        Assumes that rows with less than three fields means either missing
        first, last, or email.
        """
        for num, row in enumerate(self.rows):
            if len(row) < 3:
                x = self.rows.pop(num)
                self.manual_repair.append(x)

        # Remove all rows that don't have an email address. [q2]
        for num, row in enumerate(self.rows): 
            bad = True
            for field in row:
                if '@' in field:
                    bad = False
                    break
            if bad == True:
                x = self.rows.pop(num)
                self.manual_repair.append(x)

    def columnize(self):
        """If there's no title (Mr, Mrs, etc), put a space in the first column.
        """
        titles = [
        'Mr', 'Mrs', 'Mr.', 'Mrs.', 'mr',
        'mrs', 'mr.', 'mrs.', 'Miss', 'miss'
        ]

        for row in self.rows:
            if set(row).isdisjoint(set(titles)):
                row.insert(0, '')

    def write_csv(self, rows, name_to_write):
        """Writes a csv based on a list of lists as data for the rows, and a
        name of the file to write (string).
        """
        f = open(name_to_write, 'wt')
        try:
            writer = csv.writer(f)
            writer.writerow(('Title', 'First', 'Middle', 'Last', 'Email'))
            for row in rows:
                writer.writerow(row)
        finally:
            f.close()

if __name__ == "__main__":
    x = CleanCsv(sys.argv)
    x.do_scrub()
